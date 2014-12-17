from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
import psutil
from psutil import NoSuchProcess
from datetime import datetime
from time import sleep

import logging

from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from farmgui.models import Base
from farmgui.models import FieldSetting

from farmgui.communication import get_redis_conn
from farmgui.communication import get_redis_number

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
        logging.info('FS: Initializing')
        self.db_session = db_sm(expire_on_commit=False, autoflush=False)
        self.loop_time = FieldSetting.get_loop_time(self.db_session)
        logging.info('FS: Starting Periphery Controller')
        self.pc = PeripheryControllerWorker(config_uri)
        self.wdpc = self.pc.watchdog_key
        self.pc.start()
        self.mpc = psutil.Process(self.pc.pid)
        # wait for pc to start working (i.e. reset watchdog)
        while get_redis_number(self.redis_conn, self.wdpc) != 1:
            sleep(0.25)
        logging.info('FS: Starting Farm Manager')
        self.fm = FarmManager(config_uri)
        self.wdfm = self.fm.watchdog_key
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
        # wait for farm manager to start working
        while get_redis_number(self.redis_conn, self.wdfm) != 1:
            sleep(0.25)
        logging.info('FS: Initialisation finished\n\n')

    def work(self):
        logging.info('FS: Entered work loop')
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
            if get_redis_number(self.redis_conn, self.wdpc) != 1:
                logging.error('FS: restarting periphery controller: ' + str(pc_index))
                self.pc.terminate()
                self.pc.join()
                self.pc = PeripheryControllerWorker(self.config_uri)
                self.pc.start()
                self.mpc = psutil.Process(self.pc.pid)
                # wait for pc to start working
                while get_redis_number(self.redis_conn, self.wdpc) != 1:
                    sleep(0.25)
            if get_redis_number(self.redis_conn, self.wdfm) != 1:
                logging.error('FS: restarting farm manager')
                self.fm.terminate()
                self.fm.join()
                self.fm = FarmManager(self.config_uri)
                self.fm.start()
                self.mfm = psutil.Process(self.fm.pid)
                # wait for farm manager to start working
                while get_redis_number(self.redis_conn, self.wdfm) != 1:
                    sleep(0.25)
            # publish cpu and memory usage
            total_cpu = 0
            total_mem = 0
            mb_div = float(2 ** 20)
            timeout = 2 * self.loop_time

            pc_cpu = self.mpc.get_cpu_percent()
            total_cpu += pc_cpu
            self.redis_conn.setex('pc-cpu', pc_cpu, timeout)
            pc_mem = self.mpc.get_memory_info()[0] / mb_div
            total_mem += pc_mem
            self.redis_conn.setex('pc-mem', '%.2f' % pc_mem, timeout)

            fm_cpu = self.mfm.get_cpu_percent()
            total_cpu += fm_cpu
            self.redis_conn.setex('fm-cpu', fm_cpu, timeout)
            fm_mem = self.mfm.get_memory_info()[0] / mb_div
            total_mem += fm_mem
            self.redis_conn.setex('fm-mem', '%.2f' % fm_mem, timeout)

            fs_cpu = self.mfs.get_cpu_percent()
            total_cpu += fs_cpu
            self.redis_conn.setex('fs-cpu', fs_cpu, timeout)
            fs_mem = self.mfs.get_memory_info()[0] / mb_div
            total_mem += fs_mem
            self.redis_conn.setex('fs-mem', '%.2f' % fs_mem, timeout)
            if self.mps is not None:
                try:
                    ps_cpu = self.mps.get_cpu_percent()
                    ps_mem = self.mps.get_memory_info()[0] / mb_div
                except NoSuchProcess:
                    ps_cpu = 0
                    ps_mem = 0
                    self.mps = None
                total_cpu += ps_cpu
                total_mem += ps_mem
            else:
                ps_cpu = 0
                ps_mem = 0
            self.redis_conn.setex('ps-cpu', ps_cpu, timeout)
            self.redis_conn.setex('ps-mem', '%.2f' % ps_mem, timeout)
            if self.mdb is not None:
                db_cpu = self.mdb.get_cpu_percent()
                total_cpu += db_cpu
                db_mem = self.mdb.get_memory_info()[0] / mb_div
                total_mem += db_mem
            else:
                db_cpu = 0
                db_mem = 0
            self.redis_conn.setex('db-cpu', db_cpu, timeout)
            self.redis_conn.setex('db-mem', '%.2f' % db_mem, timeout)

            redis_cpu = self.mredis.get_cpu_percent()
            total_cpu += redis_cpu
            redis_mem = self.mredis.get_memory_info()[0] / mb_div
            total_mem += redis_mem
            self.redis_conn.setex('redis-cpu', redis_cpu, timeout)
            self.redis_conn.setex('redis-mem', '%.2f' % redis_mem, timeout)

            self.redis_conn.setex('total-cpu', '%.2f' % total_cpu, timeout)
            self.redis_conn.setex('total-mem', '%.2f' % total_mem, timeout)


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
