from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

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


class FarmManager(FarmProcess):
    """
    classdocs
    """

    def __init__(self, config_uri):
        FarmProcess.__init__(self, 'FM', config_uri)
        logging.info('FM: Initializing')
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
        self.handle_regulators(now)
        # listen for database changes (broadcat on redis channels)
        self.pubsub = self.redis_conn.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('parameter_changes',
                              'device_changes',
                              'calendar_changes',
                              'field_setting_changes',
                              'regulator_changes',
                              'periphery_controller_changes',
                              'component_input_changes',
                              'component_property_changes')
        logging.info('FM: initialisation finished')

    def reload_parameters(self):
        logging.info('FM: reloading parameters')
        print('FM: reloading parameters')
        self.parameters = {}
        # look for parameters with associated sensors
        for param in self.db_session.query(Parameter).filter(Parameter.sensor_id != None).all():
            # make sure sensors are active
            if param.sensor.periphery_controller.active is True:
                print('FM: using \"' + param.name + '\"')
                logging.info('FM: using \"' + str(param.name) + '\"')
                self.parameters[param.id] = param

    def handle_parameter_changes(self, msg):
        print('FM: handling parameter changes')
        logging.info('FM: handling parameter changes')
        change_type, param_id_str = msg.split(' ')
        param_id = int(param_id_str)
        if change_type == 'added':
            new_param = self.db_session.query(Parameter).filter_by(_id=param_id).one()
            if new_param.sensor is not None:
                if new_param.sensor.periphery_controller.active is True:
                    self.parameters[new_param.id] = new_param
                    logging.info('FM: adding parameter \"' + new_param.name + '\"')
                    print('FM: adding parameter \"' + new_param.name + '\"')
                else:
                    logging.info('FM: not adding parameter (inactive sensor): ' + new_param.name)
                    print('FM: not adding parameter (inactive sensor): ' + new_param.name)
            else:
                logging.info('FM: not adding parameter (not connected): ' + new_param.name)
                print('FM: not adding parameter (not connected): ' + new_param.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if param_id in self.parameters.keys():
                # refresh device
                logging.info('FM: refreshing parameter: ' + self.parameters[param_id].name)
                print('FM: refreshing parameter: ' + self.parameters[param_id].name)
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
                logging.info('FM: adding parameter: ' + new_param.name)
                print('FM: adding parameter: ' + new_param.name)
            # check if another device was using that actuator
            if look_for_duplicates:
                for pid in self.parameters:
                    if self.parameters[pid].sensor_id == self.parameters[param_id].sensor_id and pid != param_id:
                        logging.info('FM: colateral remove: ' + self.parameters[pid].name)
                        print('FM: colateral remove: ' + self.parameters[pid].name)
                        self.parameters.pop(pid, None)
                        break
        elif change_type == 'removed':
            logging.info('FM: removing parameter: ' + str(param_id))
            print('FM: removing parameter: ' + str(param_id))
            if param_id in self.parameters.keys():
                print('FM: found match in self.parameters, removing')
                print('FM: old: ' + str(self.parameters.keys()))
                param = self.parameters.pop(param_id)
                try:
                    self.db_session.expunge(param)
                except ObjectDeletedError:
                    pass
                print('FM: new: ' + str(self.parameters.keys()))

    def handle_device_changes(self, msg):
        print('FM: handling device changes')
        logging.info('FM: handling device changes')
        change_type, dev_id_str = msg.split(' ')
        dev_id = int(dev_id_str)
        if change_type == 'added':
            new_dev = self.db_session.query(Device).filter_by(_id=dev_id).one()
            if new_dev.actuator is not None:
                if new_dev.actuator.periphery_controller.active is True:
                    # device usable, add it
                    self.devices[new_dev.id] = new_dev
                    logging.info('FM: adding device: ' + new_dev.name)
                    print('FM: adding device: ' + new_dev.name)
                else:
                    logging.info('FM: not adding device (inactive controller): ' + new_dev.name)
                    print('FM: not adding device (inactive controller): ' + new_dev.name)
            else:
                logging.info('FM: not adding device (not connected): ' + new_dev.name)
                print('FM: not adding device (not connected): ' + new_dev.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if dev_id in self.devices.keys():
                # refresh device
                logging.info('FM: refreshing device: ' + self.devices[dev_id].name)
                print('FM: refreshing device: ' + self.devices[dev_id].name)
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
                logging.info('FM: adding device: ' + new_dev.name)
                print('FM: adding device: ' + new_dev.name)
            # check if another device was using that actuator
            if look_for_duplicates:
                for did in self.devices:
                    if self.devices[did].actuator_id == self.devices[dev_id].actuator_id and did != dev_id:
                        logging.info('FM: colateral remove: ' + self.devices[did].name)
                        print('FM: colateral remove: ' + self.devices[did].name)
                        self.devices.pop(did, None)
                        break
        elif change_type == 'removed':
            if dev_id in self.devices.keys():
                logging.info('removing device: ' + self.devices[dev_id].name)
                print('removing device: ' + self.devices[dev_id].name)
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
                logging.info('added ' + str(r.name))
                print('added ' + str(r.name))
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
                logging.info('using: ' + str(r.name))
                print('using: ' + r.name)
                self.regulators[r.id] = r
                self.real_regulators[r.id] = rr
                if r.order > self.max_regulation_order:
                    self.max_regulation_order = r.order
        elif change_type == 'removed':
            if r_id in self.regulators.keys():
                logging.info('removing regulator: ' + self.regulators[r_id].name)
                print('removing regulator: ' + self.regulators[r_id].name)
                self.devices.pop(r_id, None)

    def reload_devices(self):
        logging.info('FM: reloading devices')
        print('FM: reloading devices')
        self.devices = {}
        for dev in self.db_session.query(Device).filter(Device.actuator_id != None).all():
            # make sure actuators are active
            if dev.actuator.periphery_controller.active is True:
                # print('using: '+str(dev))
                logging.info('FM: using \"{name}\"'.format(name=str(dev.name)))
                print('FM: using \"{name}\"'.format(name=str(dev.name)))
                self.devices[dev.id] = dev

    def reload_regulators(self):
        logging.info('FM: reloading regulators')
        print('FM: reloading regulators')
        self.max_regulation_order = 0
        self.regulators = {}
        self.real_regulators = {}
        regs = self.db_session.query(Regulator).all()
        for reg in regs:
            real_reg = regulator_factory(reg.algorithm_name)
            real_reg.initialize(reg)
            # print('input['+inp+'] = '+str(inputs[inp])+', redis: '+reg.inputs[inp].redis_key)
            # print('maybe addind '+reg.name)
            logging.info('FM: using: ' + str(reg.name))
            print('FM: using: ' + reg.name)
            self.regulators[reg.id] = reg
            self.real_regulators[reg.id] = real_reg
            if reg.order > self.max_regulation_order:
                print('FM: setting max order: ' + str(reg.order))
                self.max_regulation_order = reg.order

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
            elif message['channel'] == b'regulator_changes':
                self.handle_regulator_changes(data)
            elif message['channel'] == b'periphery_controller_changes':
                self.handle_periphery_controller_changes(data)
            elif message['channel'] == b'component_input_changes':
                self.handle_component_input_changes(data)
            elif message['channel'] == b'component_property_changes':
                self.handle_component_property_changes(data)
            elif message['channel'] == b'field_setting_changes':
                self.handle_field_setting_changes(data)

    def handle_parameters(self, now):
        for param_key in self.parameters:
            self.parameters[param_key].update_setpoint(self.db_session, self.cultivation_start, now, self.redis_conn,
                                                       2 * self.loop_time)
            self.parameters[param_key].update_value(self.db_session, self.redis_conn, now, 2 * self.loop_time)

    def handle_device_setpoints(self, now):
        for dev_key in self.devices:
            self.devices[dev_key].update_setpoint(self.db_session, self.cultivation_start, now, self.redis_conn,
                                                  2 * self.loop_time)

    def handle_device_values(self, now):
        for dev_key in self.devices:
            dev = self.devices[dev_key]
            if dev.inputs['value'].connected_output is not None:
                dev.update_value(self.db_session, self.redis_conn, now, 2 * self.loop_time)
            elif dev.outputs['setpoint'].value is not None:
                self.redis_conn.setex(dev.actuator.redis_key, dev.outputs['setpoint'].value, 2 * self.loop_time)
            # dev.log_value(now, self.redis_conn)

    def handle_regulators(self, now):
        for order in range(self.max_regulation_order + 1):
            for reg_key in self.regulators:
                regulator = self.regulators[reg_key]
                real_regulator = self.real_regulators[reg_key]
                if regulator.order == order:
                    inputs = {'now': now}
                    for inp in regulator.inputs:
                        inputs[inp] = get_redis_number(self.redis_conn, regulator.inputs[inp].redis_key)
                    outputs = real_regulator.execute(inputs)
                    for outp in regulator.outputs:
                        self.redis_conn.setex(regulator.outputs[outp].redis_key, str(outputs[outp]), 2 * self.loop_time)

    def work(self, now):
        self.handle_messages()
        self.handle_parameters(now)
        self.handle_device_setpoints(now)
        self.handle_regulators(now)
        self.handle_device_values(now)
        try:
            self.db_session.commit()
        except IntegrityError as e:
            print('\n\nError: ' + str(e) + '\n\n')
            self.db_session.rollback()

