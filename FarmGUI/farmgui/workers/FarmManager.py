from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep

import logging

from redis import Redis
from pyramid.paster import get_appsettings

redis_conn = Redis('localhost', 6379)

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import PeripheryController
from ..models import Parameter
from ..models import ParameterLog
from ..models import FieldSetting
from ..models import Regulator


class FarmManager(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.db_session = db_sm()
        self.parameters = self.db_session.query(Parameter).all()
        self.regulators = self.db_session.query(Regulator).all()
        self.get_cultivation_start()
        # listen for changes in measurements (and controller connections)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('periphery_controller_changes',
                              'parameter_changes',
                              'calendar_changes',
                              'field_setting_changes',
                              'regulator_changes',
                              'log_measurements')
        present = datetime.now()
        self.schedule = {}
        self.parameter_calendars = {}
        self.recalculate_parameter_calendars(present)
        self.parameter_setpoints = {}
        self.recalculate_measurement_schedule()
        logging.info('Farm Manager initialized')

    def recalculate_parameter_calendars(self, present):
        for param in self.parameters:
            start_time = self.cultivation_start
            self.parameter_calendars[param.id] = self.current_calendar_entry(param, start_time, present)

    def current_calendar_entry(self, param, start_time, present):
        for entry in param.calendar:
            end_time = start_time + timedelta(seconds=entry.interpolation.end_time)
            if end_time > present:
                # found current calendar entry
                return {'entry': entry,
                        'start_time': start_time,
                        'end_time': end_time}
            else:
                start_time = end_time

    def calculate_parameter_setpoints(self, present):
        """

        :param present:
        """
        for param in self.parameters:
            calendar = self.parameter_calendars[param.id]
            if calendar is not None:
                if calendar['end_time'] < present:
                    # update parameter_calendars
                    self.parameter_calendars[param.id] = self.current_calendar_entry(param, present)
                    calendar = self.parameter_calendars[param.id]
                entry = calendar['entry']
                start_time =calendar['start_time']
                self.parameter_setpoints[param.id] = entry.interpolation.get_value_at(present-start_time)

    def get_cultivation_start(self):
        time_str = self.db_session.query(FieldSetting).filter_by(name='cultivation_start').first().value
        self.cultivation_start = datetime.strptime(time_str, "%d.%m.%Y")


    def calculate_actuator_setpoints(self):
        """


        """
        for r in self.regulators:
            try:
                sp = self.parameter_setpoints[r.input_parameter.id]
            except KeyError:
                sp = None
                logging.warn('no setpoint for ' + r.name + '->' + r.input_parameter.name)
            val = float(self.redis_conn.get('s'+str(r.input_parameter.sensor_id)))
            logging.debug(r.name+': sp='+str(sp)+' val='+str(val))
            if sp is not None and val is not None:
                y = r.calculate_output(sp, val, 0.5)
                logging.debug(' y: '+str(y))
                self.set_actuator(r.output_device, y)

    def set_actuator(self, device, value):
        """

        :param param:
        """
        channel_name = 'periphery_controller_' + str(device.actuator.periphery_controller_id)
        data = {'cmd': 'a' + device.actuator.name + ' ' + str(int(value)),
                'result_channel': 'log_devices',
                'caller_id': device.id}
        self.redis_conn.publish(channel_name, data)

    def work(self):
        logging.info('Farm Manager entered work loop')
        # main loop
        while True:
            # get time
            now = datetime.now()
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                if message['channel'] == b'parameter_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.recalculate_measurement_schedule()
                    logging.info('recalculated measurement schedule due to parameter changes')
                if message['channel'] == b'periphery_controller_changes':
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.recalculate_measurement_schedule()
                    logging.info('recalculated measurement schedule due to periphery controller changes')
                if message['channel'] == b'log_measurements':
                    data = eval(message['data'])
                    self.save_data(data)
                if message['channel'] == b'calendar_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.parameters = self.db_session.query(Parameter).all()
                    self.recalculate_parameter_calendars(now)
                    logging.info('recalculated parameter calendars due to calendar changes')
                elif message['channel'] == b'field_setting_changes':
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.get_cultivation_start()
                    self.recalculate_parameter_calendars(now)
                    logging.info('recalculated prarameter calendars due to field setting changes')
                if message['channel'] == b'regulator_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.regulators = self.db_session.query(Regulator).all()

            self.calculate_parameter_setpoints(now)
            self.calculate_actuator_setpoints()
            for sc in self.schedule:
                if self.schedule[sc] < now:
                    # log sensor value
                    val = self.redis_conn.get('s'+str(sc.sensor_id))
                    self.save_data(sc, now, val)
                    self.schedule[sc] = now + timedelta(seconds=sc.interval)
            sleep(0.1)

    def recalculate_measurement_schedule(self):
        logging.info('recalculating schedule')
        new_schedule = {}
        # get active controllers
        controllers = self.db_session.query(PeripheryController).filter_by(active=True).all()
        # get ids of present sensors
        sensor_ids = []
        for controller in controllers:
            for sensor in controller.sensors:
                sensor_ids.append(sensor.id)
        if len(sensor_ids) > 0:
            # get measurements with present sensors
            parameters = self.db_session.query(Parameter).filter(Parameter.sensor_id.in_(sensor_ids))
            # schedule measurements
            for p in parameters:
                new_schedule[p] = datetime.now() + timedelta(seconds=p.interval)
                logging.info(
                    'every ' + str(p.interval) + ' seconds measure: ' + p.name + ' of ' + p.component.name)
        else:
            logging.info('no measurements to schedule')
        self.schedule = new_schedule

    def save_data(self, param, time, value):
        log = ParameterLog(param, time, value)
        self.db_session.add(log)
        self.db_session.commit()


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
    logging.basicConfig(filename=settings['log_directory']+'/farm_manager.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)
    worker = FarmManager(db_sessionmaker, redis_conn)
    worker.work()
