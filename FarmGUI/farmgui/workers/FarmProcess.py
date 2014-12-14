from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from multiprocessing import Process

import logging

from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from farmgui.models import Base
from farmgui.models import FieldSetting

from farmgui.communication import get_redis_conn
from farmgui.communication import get_redis_number

from farmgui.regulators import regulator_factory


class FarmProcess(Process):
    """
    classdocs
    """

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
        self.redis_conn.setex(self.watchdog_key, 1, 3*self.loop_time)

    @property
    def watchdog_key(self):
        return self.name+'_status'
