from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
from time import sleep

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError

from farmgui.models import Parameter
from farmgui.models import Device
from farmgui.models import FieldSetting
from farmgui.models import Regulator
from farmgui.models import ComponentInput
from farmgui.models import ComponentProperty

from farmgui.communication import get_redis_number

from farmgui.regulators import regulator_factory

from farmgui.workers import FarmProcess


class FarmLogger(FarmProcess):
    """
    classdocs
    """

    def __init__(self, config_uri):
        FarmProcess.__init__(self, 'FL', config_uri)
        logging.info('Initializing Farm Logger')
        self.parameters = None
        self.devices = None
        now = datetime.now()
        # query database
        self.reload_parameters()
        self.reload_devices()
        self.handle_parameters()
        self.handle_devices()
        # listen for database changes (broadcat on redis channels)
        self.pubsub = self.redis_conn.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('parameter_changes',
                              'device_changes',
                              'field_setting_changes')
        logging.info('Farm Logger initialized\n\n')

    def reload_parameters(self):
        logging.info('FL: reloading parameters')
        print('FL: reloading parameters')
        self.parameters = []
        # look for parameters with associated sensors
        for param in self.db_session.query(Parameter).filter(Parameter.sensor_id != None).all():
            # make sure sensors are active
            if param.sensor.periphery_controller.active is True:
                print('FL: using: ' + param.name)
                logging.info('FL: using: ' + str(param.name))
                self.parameters.append(param)

    def handle_parameter_changes(self, msg):
        print('FL: handling parameter changes')
        logging.info('FL: handling parameter changes')
        change_type, param_id_str = msg.split(' ')
        param_id = int(param_id_str)
        if change_type == 'added':
            new_param = self.db_session.query(Parameter).filter_by(_id=param_id).one()
            if new_param.sensor is not None:
                if new_param.sensor.periphery_controller.active is True:
                    self.parameters.append(new_param)
                    logging.info('FL: adding parameter: ' + new_param.name)
                    print('FL: adding parameter: ' + new_param.name)
                else:
                    logging.info('FL: not adding parameter (inactive sensor): ' + new_param.name)
                    print('FL: not adding parameter (inactive sensor): ' + new_param.name)
            else:
                logging.info('FL: not adding parameter (not connected): ' + new_param.name)
                print('FL: not adding parameter (not connected): ' + new_param.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if param_id in self.parameters.keys():
                # refresh device
                logging.info('FL: refreshing parameter: ' + self.parameters[param_id].name)
                print('FL: refreshing parameter: ' + self.parameters[param_id].name)
                self.db_session.refresh(self.parameters[param_id])
                if self.parameters[param_id].sensor_id is not None:
                    if not self.parameters[param_id].sensor.periphery_controller.active:
                        self.parameters.pop(param_id, None)
                        look_for_duplicates = False
                else:
                    self.parameters.pop(param_id, None)
                    look_for_duplicates = False
            else:
                new_param = self.db_session.query(Parameter).filter_by(_id=param_id).one()
                self.parameters[new_param.id] = new_param
                logging.info('adding parameter: ' + new_param.name)
                print('adding parameter: ' + new_param.name)
            # check if another device was using that actuator
            if look_for_duplicates:
                for pid in self.parameters:
                    if self.parameters[pid].sensor_id == self.parameters[param_id].sensor_id and pid != param_id:
                        logging.info('colateral remove: ' + self.parameters[pid].name)
                        print('colateral remove: ' + self.parameters[pid].name)
                        self.parameters.pop(pid, None)
                        break
        elif change_type == 'removed':
            logging.info('removing parameter: ' + str(param_id))
            print('removing parameter: ' + str(param_id))
            if param_id in self.parameters.keys():
                print('found match in self.parameters, removing')
                print('old: ' + str(self.parameters.keys()))
                param = self.parameters.pop(param_id)
                try:
                    self.db_session.expunge(param)
                except ObjectDeletedError:
                    pass
                print('new: ' + str(self.parameters.keys()))

    def handle_device_changes(self, msg):
        print('handling device changes')
        logging.info('handling device changes')
        change_type, dev_id_str = msg.split(' ')
        dev_id = int(dev_id_str)
        if change_type == 'added':
            new_dev = self.db_session.query(Device).filter_by(_id=dev_id).one()
            if new_dev.actuator is not None:
                if new_dev.actuator.periphery_controller.active is True:
                    # device usable, add it
                    self.devices[new_dev.id] = new_dev
                    logging.info('adding device: ' + new_dev.name)
                    print('adding device: ' + new_dev.name)
                else:
                    logging.info('not adding device (inactive controller): ' + new_dev.name)
                    print('not adding device (inactive controller): ' + new_dev.name)
            else:
                logging.info('not adding device (not connected): ' + new_dev.name)
                print('not adding device (not connected): ' + new_dev.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if dev_id in self.devices.keys():
                # refresh device
                logging.info('refreshing device: ' + self.devices[dev_id].name)
                print('refreshing device: ' + self.devices[dev_id].name)
                self.db_session.refresh(self.devices[dev_id])
                if self.devices[dev_id].actuator_id is not None:
                    if not self.devices[dev_id].actuator.periphery_controller.active:
                        self.devices.pop(dev_id, None)
                        look_for_duplicates = False
                else:
                    self.devices.pop(dev_id, None)
                    look_for_duplicates = False
            else:
                new_dev = self.db_session.query(Device).filter_by(_id=dev_id).one()
                self.devices[new_dev.id] = new_dev
                logging.info('adding device: ' + new_dev.name)
                print('adding device: ' + new_dev.name)
            # check if another device was using that actuator
            if look_for_duplicates:
                for did in self.devices:
                    if self.devices[did].actuator_id == self.devices[dev_id].actuator_id and did != dev_id:
                        logging.info('colateral remove: ' + self.devices[did].name)
                        print('colateral remove: ' + self.devices[did].name)
                        self.devices.pop(did, None)
                        break
        elif change_type == 'removed':
            if dev_id in self.devices.keys():
                logging.info('removing device: ' + self.devices[dev_id].name)
                print('removing device: ' + self.devices[dev_id].name)
                self.devices.pop(dev_id, None)

    def handle_field_setting_changes(self, msg):
        if msg == 'loop_time':
            self.loop_time = FieldSetting.get_loop_time(self.db_session)
        elif msg == 'cultivation_start':
            self.cultivation_start = FieldSetting.get_cultivation_start(self.db_session)
            # make shure calendars are recomputed
            for key in self.parameters:
                self.parameters[key].current_calendar_entry = None
            for key in self.devices:
                self.devices[key].current_calendar_entry = None

    def reload_devices(self):
        logging.info('reloading devices')
        print('reloading devices')
        self.devices = {}
        for dev in self.db_session.query(Device).filter(Device.actuator_id != None).all():
            # make sure actuators are active
            if dev.actuator.periphery_controller.active is True:
                # print('using: '+str(dev))
                logging.info('using: ' + str(dev.name))
                print('using: ' + str(dev.name))
                self.devices[dev.id] = dev

    def handle_messages(self):
        message = self.pubsub.get_message()
        if message is not None:
            # something in the database changed
            data = message['data'].decode('UTF-8')
            print('\n\nmessage: ' + str(message))
            if message['channel'] == b'parameter_changes':
                self.handle_parameter_changes(data)
            elif message['channel'] == b'device_changes':
                self.handle_device_changes(data)
            elif message['channel'] == b'field_setting_changes':
                self.handle_field_setting_changes(data)

    def handle_parameters(self, now):
        for param_key in self.parameters:
            self.parameters[param_key].update_setpoint(self.db_session, self.cultivation_start, now, self.redis_conn,
                                                       2 * self.loop_time)
            self.parameters[param_key].update_value(self.db_session, self.redis_conn, now, 2 * self.loop_time)

    def handle_devices(self, now):
        for dev_key in self.devices:
            self.devices[dev_key].update_setpoint(self.db_session, self.cultivation_start, now, self.redis_conn,
                                                  2 * self.loop_time)
            self.devices[dev_key].update_value(self.db_session, self.redis_conn, now, 2 * self.loop_time)
            # self.devices[dev_key].log_value(now, self.redis_conn)

    def run(self):
        logging.info('Farm Logger entered work loop')
        print('Farm Logger entered work loop')
        last_run = datetime.now()
        while True:
            # sleep
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            t0 = datetime.now()
            now = FarmProcess.unprecise_now(datetime.now())
            last_run = now
            self.handle_messages()
            # calculate setpoints, log parameters
            self.handle_parameters(now)
            self.handle_devices(now)
            try:
                self.db_session.commit()
            except IntegrityError as e:
                print('\n\nError: ' + str(e) + '\n\n')
                self.db_session.rollback()
            self.reset_watchdog()
            worktime = datetime.now() - t0
            if worktime > self.loop_time:
                logging.error('FL: t_w=%.2f ' % worktime.total_seconds())

