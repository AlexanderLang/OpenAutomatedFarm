from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep

import logging

from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from farmgui.models import Base
from farmgui.models import Parameter
from farmgui.models import Device
from farmgui.models import FieldSetting
from farmgui.models import Regulator
from farmgui.models import ComponentInput
from farmgui.models import ComponentProperty

from farmgui.communication import get_redis_conn
from farmgui.communication import get_redis_number

from farmgui.regulators import regulator_factory


class FarmManager(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.loop_time = timedelta(seconds=1)
        self.db_session = self.db_sessionmaker(expire_on_commit=False, autoflush=False)
        self.parameters = None
        self.regulators = None
        self.real_regulators = None
        self.devices = None
        self.max_regulation_order = 0
        now = datetime.now()
        # query database
        self.cultivation_start = FieldSetting.get_cultivation_start(self.db_session)
        self.reload_parameters()
        self.reload_devices()
        self.handle_parameters(now)
        self.handle_device_setpoints(now)
        self.reload_regulators()
        self.handle_regulators()
        # listen for database changes (broadcat on redis channels)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('parameter_changes',
                              'device_changes',
                              'calendar_changes',
                              'field_setting_changes',
                              'regulator_changes',
                              'periphery_controller_changes',
                              'component_input_changes',
                              'component_property_changes')
        logging.info('Farm Manager initialized')

    def reload_parameters(self):
        logging.info('reloading parameters')
        print('reloading parameters')
        self.parameters = {}
        # look for parameters with associated sensors
        for param in self.db_session.query(Parameter).filter(Parameter.sensor_id != None).all():
            # make sure sensors are active
            if param.sensor.periphery_controller.active is True:
                print('using: '+param.name)
                logging.info('using: '+str(param))
                self.parameters[param.id] = param

    def handle_parameter_changes(self, msg):
        print('handling parameter changes')
        logging.info('handling parameter changes')
        change_type, param_id_str = msg.split(' ')
        param_id = int(param_id_str)
        if change_type == 'added':
            new_param = self.db_session.query(Parameter).filter_by(_id=param_id).one()
            if new_param.sensor is not None:
                if new_param.sensor.periphery_controller.active is True:
                    self.parameters[new_param.id] = new_param
                    logging.info('adding parameter: '+new_param.name)
                    print('adding parameter: '+new_param.name)
                else:
                    logging.info('not adding parameter (inactive sensor): '+new_param.name)
                    print('not adding parameter (inactive sensor): '+new_param.name)
            else:
                logging.info('not adding parameter (not connected): '+new_param.name)
                print('not adding parameter (not connected): '+new_param.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if param_id in self.parameters.keys():
                # refresh device
                logging.info('refreshing parameter: '+self.parameters[param_id].name)
                print('refreshing parameter: '+self.parameters[param_id].name)
                self.db_session.refresh(self.parameters[param_id])
                if self.parameters[param_id].sensor_id is not None:
                    if self.parameters[param_id].sensor.periphery_controller.active == False:
                        self.parameters.pop(param_id, None)
                        look_for_duplicates = False
                else:
                    self.parameters.pop(param_id, None)
                    look_for_duplicates = False
            else:
                new_param = self.db_session.query(Parameter).filter_by(_id=param_id).one()
                self.parameters[new_param.id] = new_param
                logging.info('adding parameter: '+new_param.name)
                print('adding parameter: '+new_param.name)
            # check if another device was using that actuator
            if look_for_duplicates:
                for pid in self.parameters:
                    if self.parameters[pid].sensor_id == self.parameters[param_id].sensor_id and pid != param_id:
                        logging.info('colateral remove: '+self.parameters[pid].name)
                        print('colateral remove: '+self.parameters[pid].name)
                        self.parameters.pop(pid, None)
                        break
        elif change_type == 'removed':
            if param_id in self.parameters.keys():
                logging.info('removing parameter: '+self.parameters[param_id].name)
                print('removing device: '+self.parameters[param_id].name)
                self.devices.pop(param_id, None)

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
                    logging.info('adding device: '+new_dev.name)
                    print('adding device: '+new_dev.name)
                else:
                    logging.info('not adding device (inactive controller): '+new_dev.name)
                    print('not adding device (inactive controller): '+new_dev.name)
            else:
                logging.info('not adding device (not connected): '+new_dev.name)
                print('not adding device (not connected): '+new_dev.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if dev_id in self.devices.keys():
                # refresh device
                logging.info('refreshing device: '+self.devices[dev_id].name)
                print('refreshing device: '+self.devices[dev_id].name)
                self.db_session.refresh(self.devices[dev_id])
                if self.devices[dev_id].actuator_id is not None:
                    if self.devices[dev_id].actuator.periphery_controller.active == False:
                        self.devices.pop(dev_id, None)
                        look_for_duplicates = False
                else:
                    self.devices.pop(dev_id, None)
                    look_for_duplicates = False
            else:
                new_dev = self.db_session.query(Device).filter_by(_id=dev_id).one()
                self.devices[new_dev.id] = new_dev
                logging.info('adding device: '+new_dev.name)
                print('adding device: '+new_dev.name)
            # check if another device was using that actuator
            if look_for_duplicates:
                for did in self.devices:
                    if self.devices[did].actuator_id == self.devices[dev_id].actuator_id and did != dev_id:
                        logging.info('colateral remove: '+self.devices[did].name)
                        print('colateral remove: '+self.devices[did].name)
                        self.devices.pop(did, None)
                        break
        elif change_type == 'removed':
            if dev_id in self.devices.keys():
                logging.info('removing device: '+self.devices[dev_id].name)
                print('removing device: '+self.devices[dev_id].name)
                self.devices.pop(dev_id, None)

    def handle_periphery_controller_changes(self, msg):
        change_type, pc_id_str = msg.split(' ')
        pc_id = int(pc_id_str)
        print('handling periphery controller changes:')
        if change_type == 'connected':
            self.reload_parameters()
            self.reload_devices()
            self.reload_regulators()
        if change_type == 'disconnected':
            self.reload_parameters()
            self.reload_devices()
            self.reload_regulators()

    def handle_component_input_changes(self, msg):
        print('handle component input changes')
        logging.info('handling component input changes')
        ci_id = int(msg)
        ci = self.db_session.query(ComponentInput).filter_by(_id=ci_id).one()
        if ci.component.component_type == 'device':
            self.reload_devices()
        if ci.component.component_type == 'regulator':
            if ci.component_id in self.regulators:
                reg = self.regulators[ci.component_id]
                old_order = reg.order
                self.db_session.refresh(reg)
                if old_order != reg.order:
                    self.max_regulation_order = 0
                    for reg_id in self.regulators:
                        order = self.regulators[reg_id].order
                        if order > self.max_regulation_order:
                            self.max_regulation_order = order
            else:
                reg = self.db_session.query(Regulator).filter_by(_id=ci.component_id).one()
                real_reg = regulator_factory(reg.algorithm_name)
                real_reg.initialize(reg)
                inputs = {}
                for inp in reg.inputs:
                    inputs[inp] = get_redis_number(self.redis_conn, reg.inputs[inp].redis_key)
                if real_reg.is_executable(inputs):
                    self.regulators[reg.id] = reg
                    self.real_regulators[reg.id] = real_reg

    def handle_component_property_changes(self, msg):
        print('handling component property changes')
        logging.info('handling component property changes')
        cp_id = int(msg)
        cp = self.db_session.query(ComponentProperty).filter_by(_id=cp_id).one()
        if cp.component.component_type == 'regulator':
            if cp.component_id in self.regulators:
                reg = self.regulators[cp.component_id]
                self.db_session.refresh(reg)
                real_reg = self.real_regulators[cp.component_id]
                real_reg.initialize(reg)

    def handle_regulator_changes(self, msg):
        print('handle regulator changes')
        logging.info('handling regulator changes')
        change_type, r_id_str = msg.split(' ')
        r_id = int(r_id_str)
        if change_type == 'added':
            r = self.db_session.query(Regulator).filter_by(_id=r_id).one()
            rr = regulator_factory(r.algorithm_name)
            rr.initialize(r)
            inputs = {}
            for inp in r.inputs:
                inputs[inp] = get_redis_number(self.redis_conn, r.inputs[inp].redis_key)
            if rr.is_executable(inputs):
                self.regulators[r.id] = r
                self.real_regulators[r.id] = rr
                logging.info('added '+str(r))
                print('added '+str(r))
        if change_type == 'changed':
            if r_id in self.regulators.keys():
                r = self.regulators[r_id]
                self.db_session.refresh(r)
            else:
                r = self.db_session.query(Regulator).filter_by(_id=r_id).one()
            rr = regulator_factory(r.algorithm_name)
            rr.initialize(r)
            inputs = {}
            for inp in r.inputs:
                inputs[inp] = get_redis_number(self.redis_conn, r.inputs[inp].redis_key)
            if rr.is_executable(inputs) or r.order > 0:
                logging.info('using: '+str(r))
                print('using: '+r.name)
                self.regulators[r.id] = r
                self.real_regulators[r.id] = rr
                if r.order > self.max_regulation_order:
                    self.max_regulation_order = r.order
        elif change_type == 'removed':
            if r_id in self.regulators.keys():
                logging.info('removing regulator: '+self.regulators[r_id].name)
                print('removing regulator: '+self.regulators[r_id].name)
                self.devices.pop(r_id, None)

    def reload_devices(self):
        logging.info('reloading devices')
        print('reloading devices')
        self.devices = {}
        for dev in self.db_session.query(Device).filter(Device.actuator_id != None).all():
            # make sure actuators are active
            if dev.actuator.periphery_controller.active is True:
                #print('using: '+str(dev))
                logging.info('using: '+str(dev.name))
                print('using: '+str(dev.name))
                self.devices[dev.id] = dev

    def reload_regulators(self):
        logging.info('reloading regulators')
        print('reloading regulators')
        self.max_regulation_order = 0
        self.regulators = {}
        self.real_regulators = {}
        regs = self.db_session.query(Regulator).all()
        for reg in regs:
            real_reg = regulator_factory(reg.algorithm_name)
            real_reg.initialize(reg)
                #print('input['+inp+'] = '+str(inputs[inp])+', redis: '+reg.inputs[inp].redis_key)
            #print('maybe addind '+reg.name)
            logging.info('using: '+str(reg))
            print('using: '+reg.name)
            self.regulators[reg.id] = reg
            self.real_regulators[reg.id] = real_reg
            if reg.order > self.max_regulation_order:
                print('setting max order: '+str(reg.order))
                self.max_regulation_order = reg.order

    def handle_messages(self):
        message = self.pubsub.get_message()
        if message is not None:
            # something in the database changed
            data = message['data'].decode('UTF-8')
            print('\n\nmessage: '+str(message))
            if message['channel'] == b'parameter_changes':
                self.handle_parameter_changes(data)
            elif message['channel'] == b'device_changes':
                self.handle_device_changes(data)
            elif message['channel'] == b'regulator_changes':
                self.handle_regulator_changes(data)
            elif message['channel'] == b'periphery_controller_changes':
                self.handle_periphery_controller_changes(data)
            elif message['channel'] == b'component_input_changes':
                self.handle_component_input_changes(data)
            elif message['channel'] == b'component_property_changes':
                self.handle_component_property_changes(data)

    def handle_parameters(self, now):
        for param_key in self.parameters:
            self.parameters[param_key].update_setpoint(self.cultivation_start, now, self.redis_conn)
            self.parameters[param_key].update_value(self.redis_conn)
            self.parameters[param_key].log_value(now, self.redis_conn)
            self.parameters[param_key].log_setpoint(now, self.redis_conn)

    def handle_device_setpoints(self, now):
        for dev_key in self.devices:
            self.devices[dev_key].update_setpoint(self.cultivation_start, now, self.redis_conn)

    def handle_device_values(self, now):
        for dev_key in self.devices:
            self.devices[dev_key].update_value(self.redis_conn)
            self.devices[dev_key].log_value(now, self.redis_conn)

    def handle_regulators(self):
        for order in range(self.max_regulation_order + 1):
            for reg_key in self.regulators:
                regulator = self.regulators[reg_key]
                real_regulator = self.real_regulators[reg_key]
                if regulator.order == order:
                    inputs = {}
                    for inp in regulator.inputs:
                        inputs[inp] = get_redis_number(self.redis_conn, regulator.inputs[inp].redis_key)
                    outputs = real_regulator.execute(inputs)
                    for outp in regulator.outputs:
                        self.redis_conn.setex(regulator.outputs[outp].redis_key, str(outputs[outp]), 2*self.loop_time)

    def work(self):
        logging.info('Farm Manager entered work loop')
        last_run = datetime.now()
        loop_counter = 0
        while True:
            loop_counter += 1
            # sleep
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            now = datetime.now()
            last_run = now
            self.handle_messages()
            self.db_session.commit()
            # calculate setpoints, log parameters
            self.handle_parameters(now)
            self.handle_device_setpoints(now)
            self.handle_regulators()
            self.handle_device_values(now)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s\n'
          '(example: "%s")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    settings = get_appsettings(config_uri)
    db_engine = engine_from_config(settings, 'sqlalchemy.')
    db_sessionmaker = sessionmaker(bind=db_engine)
    Base.metadata.bind = db_engine
    redis_conn = get_redis_conn(config_uri)
    logging.basicConfig(filename=settings['log_directory'] + '/farm_manager.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)
    worker = FarmManager(db_sessionmaker, redis_conn)
    worker.work()
