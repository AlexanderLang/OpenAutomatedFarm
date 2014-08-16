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
from ..models import Regulator


class ControlLoop(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.db_session = db_sm()
        self.regulators = self.db_session.query(Regulator).all()
        for reg in self.regulators:
            reg.esum = 0
        # listen for changes in calendar (and controller connections)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('regulator_changes')

    def work(self):
        # main loop
        while True:
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                if message['channel'] == b'regulator_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.regulators = self.db_session.query(Regulator).all()

            self.calculate_setpoints()
            sleep(0.5)

    def calculate_setpoints(self):
        for r in self.regulators:
            sp = float(self.redis_conn.get('sp'+str(r.input_parameter_id)))
            val = float(self.redis_conn.get('s'+str(r.input_parameter.sensor_id)))
            y = r.calculate_output(sp, val, 0.5)
            print('output: '+str(y))
            self.set_actuator(r.output_device, y)

    def set_actuator(self, device, value):
        """

        :param param:
        """
        channel_name = 'periphery_controller_' + str(device.actuator.periphery_controller_id)
        data = {'cmd': 'a' + device.actuator.name + ' ' + str(value),
                'result_channel': 'log_devices',
                'caller_id': device.id}
        self.redis_conn.publish(channel_name, data)


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
    worker = ControlLoop(db_sessionmaker, redis_conn)
    worker.work()
