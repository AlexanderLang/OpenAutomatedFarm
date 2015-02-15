from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from time import sleep

import logging

from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from farmgui.models import Base
from farmgui.models import FieldSetting

from farmgui.communication import get_redis_conn

from farmgui.workers import farm_process_generator
from farmgui.workers.ProcessMonitor import ProcessMonitor


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
    # setup logging
    logging.basicConfig(filename=settings['log_directory'] + '/oafd.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)
    logging.info('D: Initializing')
    # connect to database
    db_engine = engine_from_config(settings, 'sqlalchemy.')
    db_sessionmaker = sessionmaker(bind=db_engine)
    Base.metadata.bind = db_engine
    db_session = db_sessionmaker(expire_on_commit=False, autoflush=False)
    # connect to redis
    redis_conn = get_redis_conn(config_uri)

    loop_time = FieldSetting.get_loop_time(db_session)
    process_timeout = 30 * loop_time

    logging.info('D: starting farm processes')
    children = []
    for proc in farm_process_generator(config_uri, redis_conn, process_timeout):
        children.append((proc, ProcessMonitor(proc.worker.pid, proc.worker.name, redis_conn, loop_time)))

    logging.info('D: Initialisation finished')
    last_run = datetime.now() - loop_time
    while True:
        # sleep
        while datetime.now() - last_run < loop_time:
            sleep(0.05)
        last_run = datetime.now()
        # make sure all processes are running and update monitors
        for proc, mon in children:
            if not proc.check_watchdog():
                proc.restart()
                mon.change_pid(proc.worker.pid)
            mon.update()

