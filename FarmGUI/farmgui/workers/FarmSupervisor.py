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
        self.pcids = []
        self.mpcs = []
        self.loop_time = FieldSetting.get_loop_time(self.db_session)
        for dev in self.devs:
            pc = PeripheryControllerWorker(dev, config_uri)
            self.pcs.append(pc)
            self.pcids.append(pc.periphery_controller.id)
            pc.start()
            self.mpcs.append(psutil.Process(pc.pid))
        self.fm = FarmManager(config_uri)
        self.fm.start()
        self.mfm = psutil.Process(self.fm.pid)
        self.mfs = psutil.Process(os.getpid())
        # look for other interesting processes
        self.mps = None
        self.mdb = None
        self.mredis = None
        for proc in psutil.process_iter():
            if proc.name() == 'pserve':
                self.mps = psutil.Process(proc.pid)
            elif proc.name() == 'mysqld':
                self.mdb = psutil.Process(proc.pid)
            elif proc.name() == 'redis-server':
                self.mredis = psutil.Process(proc.pid)
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
            # publish cpu and memory usage
            mb_div = float(2 ** 20)
            timeout = 2 * self.loop_time
            fm_cpu = self.mfm.get_cpu_percent()
            self.redis_conn.setex('fm-cpu', fm_cpu, timeout)
            fm_mem = self.mfm.get_memory_info()[0] / mb_div
            self.redis_conn.setex('fm-mem', fm_mem, timeout)
            fs_cpu = self.mfs.get_cpu_percent()
            self.redis_conn.setex('fs-cpu', fs_cpu, timeout)
            fs_mem = self.mfs.get_memory_info()[0] / mb_div
            self.redis_conn.setex('fs-mem', fs_mem, timeout)
            if self.mps is not None:
                ps_cpu = self.mps.get_cpu_percent()
                self.redis_conn.setex('ps-cpu', ps_cpu, timeout)
                ps_mem = self.mps.get_memory_info()[0] / mb_div
                self.redis_conn.setex('ps-mem', ps_mem, timeout)
            if self.mdb is not None:
                db_cpu = self.mdb.get_cpu_percent()
                self.redis_conn.setex('db-cpu', db_cpu, timeout)
                db_mem = self.mdb.get_memory_info()[0] / mb_div
                self.redis_conn.setex('db-mem', db_mem, timeout)
            if self.mredis is not None:
                redis_cpu = self.mredis.get_cpu_percent()
                self.redis_conn.setex('redis-cpu', redis_cpu, timeout)
                redis_mem = self.mredis.get_memory_info()[0] / mb_div
                self.redis_conn.setex('redis-mem', redis_mem, timeout)
            for pc_index in range(len(self.mpcs)):
                pc_cpu = self.mpcs[pc_index].get_cpu_percent()
                self.redis_conn.setex('pc-cpu-'+str(self.pcids[pc_index]), pc_cpu, timeout)
                pc_mem = self.mpcs[pc_index].get_memory_info()[0] / mb_div
                self.redis_conn.setex('pc-mem-'+str(self.pcids[pc_index]), pc_mem, timeout)


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
