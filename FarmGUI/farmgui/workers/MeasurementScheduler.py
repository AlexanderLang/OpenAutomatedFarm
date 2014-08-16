from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep

import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s', datefmt='%Y.%m.%d %I:%M', level=logging.INFO)

from redis import Redis
from pyramid.paster import get_appsettings

redis_conn = Redis('localhost', 6379)

from sqlalchemy import desc
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import PeripheryController
from ..models import Parameter
from ..models import ParameterLog


class MeasurementScheduler(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        # listen for changes in measurements (and controller connections)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('periphery_controller_changes', 'parameter_changes', 'log_measurements')
        self.schedule = {}
        self.db_session = self.db_sessionmaker()
        self.recalculate_schedule()

    def work(self):
        # main loop
        while True:
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                if message['channel'] == b'parameter_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.recalculate_schedule()
                if message['channel'] == b'periphery_controller_changes':
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.recalculate_schedule()
                if message['channel'] == b'log_measurements':
                    data = eval(message['data'])
                    self.save_data(data)
            # get time
            now = datetime.now()
            # print(str(now)+':')
            for sc in self.schedule:
                if self.schedule[sc] < now:
                    # log sensor value
                    val = self.redis_conn.get('s'+str(sc.sensor_id))
                    self.save_data(sc, now, val)
                    self.schedule[sc] = now + timedelta(seconds=sc.interval)
            sleep(0.5)

    def recalculate_schedule(self):
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
        #print('oaf_ms: saved ' + str(log))


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
    worker = MeasurementScheduler(db_sessionmaker, redis_conn)
    worker.work()
