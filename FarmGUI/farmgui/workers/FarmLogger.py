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
        logging.info('Farm Manager initialized\n\n')

    def reload_parameters(self):
        logging.info('reloading parameters')
        print('reloading parameters')
        self.parameters = {}
        # look for parameters with associated sensors
        for param in self.db_session.query(Parameter).filter(Parameter.sensor_id != None).all():
            # make sure sensors are active
            if param.sensor.periphery_controller.active is True:
                print('using: ' + param.name)
                logging.info('using: ' + str(param.name))
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
                    logging.info('adding parameter: ' + new_param.name)
                    print('adding parameter: ' + new_param.name)
                else:
                    logging.info('not adding parameter (inactive sensor): ' + new_param.name)
                    print('not adding parameter (inactive sensor): ' + new_param.name)
            else:
                logging.info('not adding parameter (not connected): ' + new_param.name)
                print('not adding parameter (not connected): ' + new_param.name)
        elif change_type == 'changed':
            look_for_duplicates = True
            if param_id in self.parameters.keys():
                # refresh device
                logging.info('refreshing parameter: ' + self.parameters[param_id].name)
                print('refreshing parameter: ' + self.parameters[param_id].name)
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
            # print('input['+inp+'] = '+str(inputs[inp])+', redis: '+reg.inputs[inp].redis_key)
            # print('maybe addind '+reg.name)
            logging.info('using: ' + str(reg.name))
            print('using: ' + reg.name)
            self.regulators[reg.id] = reg
            self.real_regulators[reg.id] = real_reg
            if reg.order > self.max_regulation_order:
                print('setting max order: ' + str(reg.order))
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
            self.devices[dev_key].update_value(self.db_session, self.redis_conn, now, 2 * self.loop_time)
            # self.devices[dev_key].log_value(now, self.redis_conn)

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

    def unprecise_now(self, now):
        second = now.second
        if now.microsecond >= 500000:
            second += 1
        return datetime(now.year, now.month, now.day, now.hour, now.minute, second)

    def run(self):
        logging.info('Farm Manager entered work loop')
        print('Farm Manager entered work loop')
        last_run = datetime.now()
        loop_counter = 0
        while True:
            loop_counter += 1
            # sleep
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            t0 = datetime.now()
            now = self.unprecise_now(datetime.now())
            last_run = now
            self.handle_messages()
            t1 = datetime.now()
            t_m = t1 - t0
            # calculate setpoints, log parameters
            self.handle_parameters(now)
            t2 = datetime.now()
            t_p = t2 - t1
            self.handle_device_setpoints(now)
            t3 = datetime.now()
            t_ds = t3 - t2
            self.handle_regulators(now)
            t4 = datetime.now()
            t_r = t4 - t3
            self.handle_device_values(now)
            t5 = datetime.now()
            t_dv = t5 - t4
            try:
                self.db_session.commit()
            except IntegrityError as e:
                print('\n\nError: ' + str(e) + '\n\n')
                self.db_session.rollback()
            t6 = datetime.now()
            t_c = t6 - t5
            self.reset_watchdog()
            worktime = datetime.now() - t0
            if worktime > self.loop_time:
                msg = 'FM: t_w=%.2f ' % worktime.total_seconds()
                msg += ' t_m=%.3f t_p=%.3f' % (t_m.total_seconds(), t_p.total_seconds())
                msg += ' t_ds=%.3f t_r=%.3f' % (t_ds.total_seconds(), t_r.total_seconds())
                msg += ' t_dv=%.3f t_c=%.3f' % (t_dv.total_seconds(), t_c.total_seconds())
                logging.error(msg)
