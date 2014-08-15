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

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import Parameter
from ..models import FieldSetting


class SetpointPorvider(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.db_session = db_sm()
        self.parameters = self.db_session.query(Parameter).all()
        self.get_cultivation_start()
        # listen for changes in calendar (and controller connections)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('calendar_changes', 'field_setting_changes')

    def work(self):
        # main loop
        while True:
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                if message['channel'] == b'calendar_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.parameters = self.db_session.query(Parameter).all()
                elif message['channel'] == b'field_setting_changes':
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.get_cultivation_start()

            self.calculate_setpoints()
            sleep(0.5)

    def calculate_setpoints(self):
        present = datetime.now()
        for param in self.parameters:
            key = 'sp'+str(param.id)
            calendar_time = self.cultivation_start
            for entry in param.calendar:
                if calendar_time + timedelta(seconds=entry.interpolation.end_time) > present:
                    self.redis_conn.set(key, entry.interpolation.get_value_at(present-calendar_time))
                    break
                calendar_time = calendar_time + timedelta(seconds=entry.interpolation.end_time)

    def get_cultivation_start(self):
        time_str = self.db_session.query(FieldSetting).filter_by(name='cultivation_start').first().value
        self.cultivation_start = datetime.strptime(time_str, "%d.%m.%Y")



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
    worker = SetpointPorvider(db_sessionmaker, redis_conn)
    worker.work()
