from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys

from redis import Redis
redis_conn = Redis('localhost', 6379)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from field_controller_database import Base as Field_Controller_Base
from field_controller_database import Measurement
from field_controller_database import MeasurementLog

db_engine = create_engine('mysql+mysqlconnector://oaf:oaf_password@localhost/FieldController')
Session = sessionmaker(bind=db_engine)
db_session = Session()
Field_Controller_Base.metadata.bind = db_engine

class MeasurementLogger(object):
    '''
    classdocs
    '''
    
    def __init__(self, db_session, redis_conn):
        self.redis_conn = redis_conn
        self.db_session = db_session
        # listen for changes in measurements (and controller connections)
        self.pubsub = redis_conn.pubsub(ignore_subscribe_messages=False)
        self.pubsub.subscribe('log_measurements')
    
    def work(self):
        # main loop
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = eval(message['data'])
                m = self.db_session.query(Measurement).filter(Measurement._id == data['caller_id']).first()
                log = MeasurementLog(m, data['time'], data['value'])
                self.db_session.add(log)
                self.db_session.commit()
                print('oaf_ml: saved '+str(log))


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s\n'
          '(example: "%s")' % (cmd, cmd))
    sys.exit(1)
    
def main(argv=sys.argv):
    if len(argv) > 1:
        usage(argv)
    worker = MeasurementLogger(db_session, redis_conn)
    worker.work()
    