from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep

import logging

from serial import SerialException
from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from farmgui.models import Base
from farmgui.models import FieldSetting
from farmgui.models import ParameterType
from farmgui.models import PeripheryController
from farmgui.models import Sensor
from farmgui.models import Actuator
from farmgui.models import DeviceType

from farmgui.communication import SerialShell
from farmgui.communication import get_redis_conn


class PeripheryControllerWorker(object):
    """
    classdocs
    """

    def __init__(self, devicename, redis, db_sm):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        logging.info('\n\nInitializing Periphery Controller Worker')
        # connect with serial port
        self.serial = SerialShell(devicename)
        logging.info('connected to serial port ' + devicename)
        # register in database
        self.db_session = self.db_sessionmaker(expire_on_commit=False)
        self.loop_time = FieldSetting.get_loop_time(self.db_session)
        self.controller_id = self.serial.get_id()
        if self.controller_id == 0:
            # new controller
            self.register_new_controller(self.db_session)
        else:
            # known controller (set active)
            try:
                self.periphery_controller = self.db_session.query(PeripheryController).filter_by(_id=self.controller_id).one()
                self.periphery_controller.active = True
            except NoResultFound:
                # controller was deleted, will not be used until reset
                self.close()
                exit()
            logging.info('Working with Controller id=' + str(self.controller_id))
        self.db_session.commit()
        # let scheduler know the available sensors changed
        self.redis_conn.publish('periphery_controller_changes', 'connected '+str(self.controller_id))
        # listen for changes in the database
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('periphery_controller_changes', 'field_setting_changes')

    def register_new_controller(self, db_session):
        logging.info('Register new controller:')
        fw_name = self.serial.get_firmware_name()
        fw_version = self.serial.get_firmware_version()
        new_name = 'new ' + fw_name + ' (version ' + fw_version + ')'
        self.periphery_controller = PeripheryController(fw_name, fw_version, new_name, True)
        logging.info('\tName=\"' + new_name + '\"')
        # register sensors
        sensors = self.serial.get_sensors()
        for i in range(len(sensors)):
            s = sensors[i]
            param_type = db_session.query(ParameterType).filter_by(unit=s['unit']).first()
            self.periphery_controller.sensors.append(Sensor(self.periphery_controller, i, s['name'], param_type, s['precision'],
                                                s['min'], s['max']))
            logging.info('added sensor ' + s['name'] + ' (type=' + param_type.name + ')')
        # register actuators
        actuators = self.serial.get_actuators()
        for i in range(len(actuators)):
            a = actuators[i]
            device_type = db_session.query(DeviceType).filter_by(unit=a['unit']).first()
            self.periphery_controller.actuators.append(Actuator(self.periphery_controller, i, a['name'], device_type, a['default']))
            logging.info('added actuator ' + a['name'] + ' (type=' + device_type.name + ')')
        db_session.add(self.periphery_controller)
        db_session.flush()
        # save new id on controller
        self.controller_id = self.periphery_controller.id
        self.serial.set_id(self.controller_id)
        logging.info('saved id=' + str(self.controller_id) + ' on controller')

    def get_actuator_value_from_redis(self, actuator):
        value = self.redis_conn.get(actuator.redis_key)
        if value is None or value == b'None':
            # no setpoint, use default
            return actuator.default_value
        return float(value)

    def publish_sensor_values(self):
        try:
            values = self.serial.get_sensor_values()
            for i in range(len(self.periphery_controller.sensors)):
                sens = self.periphery_controller.sensors[i]
                self.redis_conn.setex(sens.redis_key, str(values[i]), 2*self.loop_time)
        except SerialException:
            logging.error('SerialException on publish_sensor_values')
            self.close()
            exit()

    def apply_actuator_values(self):
        values = []
        for actuator in self.periphery_controller.actuators:
            values.append(self.get_actuator_value_from_redis(actuator))
        try:
            self.serial.set_actuator_values(values)
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
                if change_type == 'deleted' and int(pc_id_str) == self.controller_id:
                    exit()
            elif message['channel'] == b'field_setting_changes':
                self.loop_time = FieldSetting.get_loop_time(self.db_session)

    def work(self):
        last_run = datetime.now()
        while True:
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            last_run = datetime.now()
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
            # let scheduler know the available sensors changed
            self.redis_conn.publish('periphery_controller_changes', 'disconnected '+str(self.controller_id))
        except NoResultFound:
            pass


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <dev_name>\n'
          '(example: "%s development.ini /dev/ttyACM0")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 3:
        usage(argv)
    config_uri = argv[1]
    dev_name = argv[2]

    settings = get_appsettings(config_uri)
    db_engine = engine_from_config(settings, 'sqlalchemy.')
    db_sessionmaker = sessionmaker(bind=db_engine)
    Base.metadata.bind = db_engine
    redis_conn = get_redis_conn(config_uri)
    logging.basicConfig(filename=settings['log_directory'] + '/pc_' + dev_name.split('/')[-1] + '.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)

    worker = PeripheryControllerWorker(dev_name, redis_conn, db_sessionmaker)
    try:
        worker.work()
    finally:
        worker.close()