from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import abc

from multiprocessing import Process

import logging
from datetime import datetime
import calendar
from time import sleep

from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from farmgui.models import Base
from farmgui.models import FieldSetting

from farmgui.communication import get_redis_conn


class FarmProcess(Process):
    """
    classdocs
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, config_uri):
        super(FarmProcess, self).__init__()
        self.name = name
        settings = get_appsettings(config_uri)
        db_engine = engine_from_config(settings, 'sqlalchemy.')
        db_sm = sessionmaker(bind=db_engine)
        Base.metadata.bind = db_engine
        logging.basicConfig(filename=settings['log_directory'] + '/farm_manager.log',
                            format='%(levelname)s:%(asctime)s: %(message)s',
                            datefmt='%Y.%m.%d %H:%M:%S',
                            level=logging.DEBUG)
        self.redis_conn = get_redis_conn(config_uri)
        self.db_sessionmaker = db_sm
        self.db_session = self.db_sessionmaker(expire_on_commit=False, autoflush=False)
        self.loop_time = FieldSetting.get_loop_time(self.db_session)

    def reset_watchdog(self):
        self.redis_conn.setex(self.watchdog_key, 1, 5*self.loop_time)

    @property
    def watchdog_key(self):
        return self.name+'_status'

    @staticmethod
    def unprecise_now(now):
        s = now.second
        m = now.minute
        h = now.hour
        d = now.day
        M = now.month
        Y = now.year
        if now.microsecond >= 500000:
            s += 1
            if s > 59:
                s = 0
                m += 1
            if m > 59:
                m = 0
                h += 1
            if h > 23:
                h = 0
                d += 1
            if d > calendar.monthrange(Y, M)[1]:
                d = 1
                M +=1
            if M > 12:
                M = 1
                Y += 1
        return datetime(Y, M, d, h, m, s)

    def run(self):
        logging.info('{name}: entered work loop'.format(name=self.name))
        print('{name}: entered work loop'.format(name=self.name))
        last_run = datetime.now() - self.loop_time
        while True:
            # sleep
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            last_run = datetime.now()
            now = FarmProcess.unprecise_now(last_run)
            self.reset_watchdog()
            self.work(now)

    @abc.abstractmethod
    def work(self, now):
        return
