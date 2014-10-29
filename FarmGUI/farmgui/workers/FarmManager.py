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

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import Parameter
from ..models import Device
from ..models import FieldSetting
from ..models import Regulator

from ..communication import get_redis_conn


class FarmManager(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.loop_time = timedelta(seconds=1)
        self.db_session = None
        self.parameters = None
        self.regulators = None
        self.devices = None
        self.cultivation_start = None
        self.max_regulation_order = 0
        self.reload_database()
        # listen for database changes (broadcat on redis channels)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('periphery_controller_changes',
                              'parameter_changes',
                              'calendar_changes',
                              'field_setting_changes',
                              'regulator_changes')
        logging.info('Farm Manager initialized')

    def reload_database(self):
        logging.info('reloading values form database')
        if self.db_session is not None:
            self.db_session.close()
        self.db_session = self.db_sessionmaker(expire_on_commit=False, autoflush=False)
        self.parameters = self.db_session.query(Parameter).all()
        self.regulators = self.db_session.query(Regulator).all()
        self.devices = self.db_session.query(Device).all()
        self.cultivation_start = FieldSetting.get_cultivation_start(self.db_session)
        self.initialize_regulators()

    def initialize_regulators(self):
        self.max_regulation_order = -1
        for regulator in self.regulators:
            #regulator.initialize()
            order = regulator.order
            print(regulator.name + ': order='+str(order))
            if order > self.max_regulation_order:
                self.max_regulation_order = order
        self.max_regulation_order += 1

    def work(self):
        logging.info('Farm Manager entered work loop')
        last_run = datetime.now()
        loop_counter = 0
        while True:
            loop_counter += 1
            # sleep
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            last_run = datetime.now()
            now = last_run
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                # something in the database changed
                self.reload_database()
            # calculate setpoints, log parameters
            for param in self.parameters:
                param.update_setpoint(self.cultivation_start, now, self.redis_conn)
                param.update_value(self.redis_conn)
                param.log_value(now, self.redis_conn)
                param.log_setpoint(now, self.redis_conn)
            for dev in self.devices:
                dev.update_setpoint(self.cultivation_start, now, self.redis_conn)
            # run regulators
            for order in range(self.max_regulation_order):
                for regulator in self.regulators:
                    if regulator.order == order:
                        regulator.execute(self.redis_conn)
            for dev in self.devices:
                dev.update_value(self.redis_conn)
                dev.log_value(now, self.redis_conn)
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
    redis_conn = get_redis_conn(config_uri)
    logging.basicConfig(filename=settings['log_directory'] + '/farm_manager.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)
    worker = FarmManager(db_sessionmaker, redis_conn)
    worker.work()
