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
from sqlalchemy.orm.exc import ObjectDeletedError

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


class FarmMonitor(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        logging.info('Farm Monitor initialized')

    def work(self):
        logging.info('Farm Monitor entered work loop')
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
            # calculate setpoints, log parameters
            self.handle_parameters(now)
            self.handle_device_setpoints(now)
            self.handle_regulators()
            self.handle_device_values(now)
            try:
                self.db_session.commit()
            except IntegrityError as e:
                print('\n\nError: '+str(e)+'\n\n')
                self.db_session.rollback()


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
