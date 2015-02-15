from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
from time import sleep

import logging
from glob import glob

from serial import SerialException

from sqlalchemy.orm.exc import NoResultFound

from farmgui.models import FieldSetting
from farmgui.models import ParameterType
from farmgui.models import PeripheryController
from farmgui.models import Sensor
from farmgui.models import Actuator
from farmgui.models import DeviceType

from farmgui.communication import SerialShell
from farmgui.communication import get_redis_number

from farmgui.workers import FarmProcess


class PeripheryControllerWorker(FarmProcess):
    """
    classdocs
    """

    def __init__(self, config_uri):
        FarmProcess.__init__(self, 'PC', config_uri)
        logging.info('PC: Initializing')
        # connect with serial port
        self.dev_names = glob('/dev/ttyA*')
        self.shells = {}
        self.controller_ids = {}
        self.periphery_controllers = {}
        for dev_name in self.dev_names:
            self.initialize_dev(dev_name)
        self.db_session.commit()
        # listen for changes in the database
        self.pubsub = self.redis_conn.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('periphery_controller_changes', 'field_setting_changes')
        logging.info('PC: Initialisation finished\n\n')

    def initialize_dev(self, dev_name):
        self.shells[dev_name] = SerialShell(dev_name)
        logging.info('connected to serial port ' + dev_name)
        # register in database
        c_id = self.shells[dev_name].get_id()
        if c_id == 0:
            # new controller
            self.register_new_controller(self.db_session, dev_name)
        else:
            # known controller (set active)
            self.controller_ids[dev_name] = c_id
            try:
                query = self.db_session.query(PeripheryController)
                self.periphery_controllers[dev_name] = query.filter_by(_id=c_id).one()
                self.periphery_controllers[dev_name].active = True
            except NoResultFound:
                # controller was deleted, will not be used until reset
                logging.error('PC: did not find id='+str(c_id)+' in database, exiting')
                self.close()
                exit()
            logging.info('Working with Controller id=' + str(self.controller_ids[dev_name]))
        # let farm know the available sensors changed
        self.redis_conn.publish('periphery_controller_changes', 'connected ' + str(self.controller_ids[dev_name]))

    def register_new_controller(self, db_session, dev_name):
        logging.info('PC: Register new controller')
        fw_name = self.shells[dev_name].get_firmware_name()
        fw_version = self.shells[dev_name].get_firmware_version()
        new_name = 'new ' + fw_name + ' (version ' + fw_version + ')'
        self.periphery_controllers[dev_name] = PeripheryController(fw_name, fw_version, new_name, True)
        logging.info('\tName=\"' + new_name + '\"')
        # register sensors
        sensors = self.shells[dev_name].get_sensors()
        for i in range(len(sensors)):
            s = sensors[i]
            param_type = db_session.query(ParameterType).filter_by(unit=s['unit']).first()
            sen = Sensor(self.periphery_controllers[dev_name], i, s['name'], param_type, s['precision'], s['min'], s['max'])
            self.periphery_controllers[dev_name].sensors.append(sen)
            logging.info('added sensor ' + s['name'] + ' (type=' + param_type.name + ')')
        # register actuators
        actuators = self.shells[dev_name].get_actuators()
        for i in range(len(actuators)):
            a = actuators[i]
            device_type = db_session.query(DeviceType).filter_by(unit=a['unit']).first()
            self.periphery_controllers[dev_name].actuators.append(
                Actuator(self.periphery_controllers[dev_name], i, a['name'], device_type, a['default']))
            logging.info('added actuator ' + a['name'] + ' (type=' + device_type.name + ')')
        db_session.add(self.periphery_controllers[dev_name])
        db_session.flush()
        # save new id on controller
        self.controller_ids[dev_name] = self.periphery_controllers[dev_name].id
        self.shells[dev_name].set_id(self.controller_ids[dev_name])
        logging.info('saved id=' + str(self.controller_ids[dev_name]) + ' on controller')
        logging.info('PC: Register new controller finished\n')

    def get_actuator_value_from_redis(self, actuator):
        value = get_redis_number(self.redis_conn, actuator.redis_key)
        if value is None:
            # no setpoint, use default
            self.redis_conn.setex(actuator.redis_key, actuator.default_value, 2 * self.loop_time)
            return actuator.default_value
        elif actuator.device_type.unit == '%':
            if value > 100:
                return 100
            elif value < 0:
                return 0
        elif actuator.device_type.unit == '0/1':
            if value == 0:
                return 0
            return 1
        return value

    def publish_sensor_values(self):
        for dev_name in self.dev_names:
            try:
                values = self.shells[dev_name].get_sensor_values()
                for i in range(len(values)):
                    sens = self.periphery_controllers[dev_name].sensors[i]
                    self.redis_conn.setex(sens.redis_key, str(values[i]), 2 * self.loop_time)
            except SerialException:
                logging.error('SerialException on publish_sensor_values')
                self.close()
                exit()

    def apply_actuator_values(self):
        for dev_name in self.dev_names:
            values = [i for i in range(len(self.periphery_controllers[dev_name].actuators))]
            for actuator in self.periphery_controllers[dev_name].actuators:
                values[actuator.index] = self.get_actuator_value_from_redis(actuator)
            try:
                self.shells[dev_name].set_actuator_values(values)
            except SerialException:
                logging.error('SerialException on apply_actuator_values')
                self.close()
                exit()

    def handle_messages(self):
        message = self.pubsub.get_message()
        if message is not None:
            # something in the database changed
            data = message['data'].decode('UTF-8')
            print('message: ' + str(message))
            if message['channel'] == b'periphery_controller_changes':
                change_type, pc_id_str = data.split(' ')
                if change_type == 'deleted':
                    dev_name = None
                    for key in self.controller_ids:
                        if self.controller_ids[key] == int(pc_id_str):
                            dev_name = key
                            break
                    try:
                        self.controller_ids.pop(dev_name)
                        self.periphery_controllers.pop(dev_name)
                        self.shells[dev_name].close()
                        self.shells.pop(dev_name)
                        self.dev_names.pop(self.dev_names.index(dev_name))
                    except KeyError:
                        pass
            elif message['channel'] == b'field_setting_changes':
                self.loop_time = FieldSetting.get_loop_time(self.db_session)

    def work(self, now):
        self.handle_messages()
        self.publish_sensor_values()
        self.apply_actuator_values()

    def close(self):
        db_session = self.db_sessionmaker()
        try:
            periphery_controller = db_session.query(PeripheryController).filter_by(_id=self.controller_id).one()
            periphery_controller.active = False
            db_session.commit()
            db_session.close()
            self.serial.close()
            # let scheduler know the available sensors changed
            self.redis_conn.publish('periphery_controller_changes', 'disconnected ' + str(self.controller_id))
        except NoResultFound:
            pass
