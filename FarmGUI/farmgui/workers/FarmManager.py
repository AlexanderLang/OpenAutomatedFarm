from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from time import sleep

import logging

from redis import Redis
from pyramid.paster import get_appsettings

redis_conn = Redis('localhost', 6379)

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import Parameter
from ..models import Device
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
        self.devices = self.db_session.query(Device).all()
        self.cultivation_start = FieldSetting.get_cultivation_start(self.db_session)
        present = datetime.now()
        for regulator in self.regulators:
            regulator.input_parameter.configure_calendar(self.cultivation_start, present)
        for device in self.devices:
            device.configure_calendar(self.cultivation_start, present)
        # listen for database changes (broadcat on redis channels)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('periphery_controller_changes',
                              'parameter_changes',
                              'calendar_changes',
                              'field_setting_changes',
                              'regulator_changes',
                              'log_measurements')
        logging.info('Farm Manager initialized')

    def work(self):
        logging.info('Farm Manager entered work loop')
        loop_time = 0.5
        # main loop
        while True:
            # get time
            now = datetime.now()
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                # something in the database changed
                logging.info('reloading values form database')
                self.db_session.close()
                self.db_session = self.db_sessionmaker()
                self.cultivation_start = FieldSetting.get_cultivation_start(self.db_session)
                self.parameters = self.db_session.query(Parameter).all()
                self.devices = self.db_session.query(Device).all()
                self.regulators = self.db_session.query(Regulator).all()
                for regulator in self.regulators:
                    regulator.input_parameter.configure_calendar(self.cultivation_start, now)
                for device in self.devices:
                    device.configure_calendar(self.cultivation_start, now)
            # log parameters
            for param in self.parameters:
                value = self.redis_conn.get('s' + str(param.sensor_id))
                param.log_measurement(now, value)
                self.db_session.commit()
            # set devices
            for device in self.devices:
                setpoint = device.get_setpoint(now)
                if setpoint is None:
                    device.configure_calendar(self.cultivation_start, now)
                    setpoint = device.get_setpoint(now)
                if setpoint is not None:
                    self.redis_conn.set('a'+str(device.id), setpoint)
            # run regulators
            for regulator in self.regulators:
                input_value = float(self.redis_conn.get('s' + str(regulator.input_parameter.sensor_id)))
                setpoint = regulator.input_parameter.get_setpoint(now)
                if setpoint is None:
                    regulator.input_parameter.configure_calendar(self.cultivation_start, now)
                    setpoint = regulator.input_parameter.get_setpoint(now)
                if setpoint is None:
                    logging.warning('regulator '+regulator.name+' cannot find a setpoint')
                else:
                    output_value = regulator.calculate_output(setpoint, input_value, loop_time)
                    self.redis_conn.set('a' + str(regulator.output_device_id), output_value)
            sleep(loop_time)


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
    logging.basicConfig(filename=settings['log_directory'] + '/farm_manager.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)
    worker = FarmManager(db_sessionmaker, redis_conn)
    worker.work()
