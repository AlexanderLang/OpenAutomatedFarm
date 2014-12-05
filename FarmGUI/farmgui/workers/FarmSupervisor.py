from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
import psutil
from datetime import datetime
from time import sleep
from glob import glob

import logging

from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from farmgui.models import Base
from farmgui.models import FieldSetting

from farmgui.communication import get_redis_conn

from farmgui.workers import FarmManager
from farmgui.workers import PeripheryControllerWorker


class FarmSupervisor(object):
    """
    classdocs
    """

    def __init__(self, db_sm, redis, config_uri):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.config_uri = config_uri
        self.db_session = db_sm(expire_on_commit=False, autoflush=False)
        self.devs = glob('/dev/ttyA*')
        self.pcs = []
        self.mpcs = []
        self.loop_time = FieldSetting.get_loop_time(self.db_session)
        for dev in self.devs:
            pc = PeripheryControllerWorker(dev, config_uri)
            self.pcs.append(pc)
            pc.start()
            self.mpcs.append(psutil.Process(pc.pid))
        self.fm = FarmManager(config_uri)
        self.fm.start()
        self.mfm = psutil.Process(self.fm.pid)
        logging.info('Farm Supervisor initialized')

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
            # make sure all processes are running
            for pc_index in range(len(self.pcs)):
                if not self.pcs[pc_index].is_alive():
                    # restart
                    restarted_pc = PeripheryControllerWorker(self.devs[pc_index], self.config_uri)
                    self.pcs[pc_index] = restarted_pc
                    restarted_pc.start()
                    self.mpcs[pc_index] = psutil.Process(restarted_pc.pid)
            if not self.fm.is_alive():
                self.fm = FarmManager(self.config_uri)
                self.fm.start()
                self.mfm = psutil.Process(self.fm.pid)
            # publish cpu usage
            fm_cpu = self.mfm.get_cpu_percent()
            self.redis_conn.setex('fm-cpu', fm_cpu, 2*self.loop_time)
            for pc_index in range(len(self.mpcs)):
                pc_cpu = self.mpcs[pc_index].get_cpu_percent()
                self.redis_conn.setex('pc-cpu-'+str(pc_index), pc_cpu, 2*self.loop_time)
            # publish memory usage
            fm_mem = self.mfm.get_memory_info()[0] / float(2 ** 20)
            self.redis_conn.setex('fm-mem', fm_mem, 2*self.loop_time)
            for pc_index in range(len(self.mpcs)):
                pc_mem = self.mpcs[pc_index].get_memory_info()[0] / float(2 ** 20)
                self.redis_conn.setex('pc-mem-'+str(pc_index), pc_mem, 2*self.loop_time)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s  <config_uri>\n'
          '(example: "%s  production.ini")' % (cmd, cmd))
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
    logging.basicConfig(filename=settings['log_directory'] + '/farm_supervisor.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)
    worker = FarmSupervisor(db_sessionmaker, redis_conn, config_uri)
    worker.work()
