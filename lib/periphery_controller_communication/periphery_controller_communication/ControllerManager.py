from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys

from redis import Redis
redis_conn = Redis('localhost', 6379)

from .SerialShell import SerialShell

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from field_controller_database import Base as Field_Controller_Base
from field_controller_database import PeripheryController
from field_controller_database import Sensor
from field_controller_database import Measurement

db_engine = create_engine('mysql+mysqlconnector://oaf:oaf_password@localhost/FieldController')
Session = sessionmaker(bind=db_engine)
db_session = Session()
Field_Controller_Base.metadata.bind = db_engine


class ControllerManager(object):
    '''
    classdocs
    '''
    
    def __init__(self, redis_conn, db_session):
        self.redis_conn = redis_conn
        self.db_session = db_session
        self.controllers = []
        # subscribe to channels
        self.pubsub = redis_conn.pubsub(ignore_subscribe_messages=False)
        self.pubsub.subscribe('controller_connections')
    
    def work(self):
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                if data['active'] == True:
                    # new controller connection
                    self.register_controller(data)
                else:
                    self.remove_controller(data)
                # let scheduler know the available sensors changed
                self.redis_conn.publish('measurement_changes', 'some data')
    
    def register_controller(self, data):
        if data['id'] == 0:
            # new controller
            new_name = 'new ' + data['fwName'] + ' (version ' + data['fwVersion'] + ')'
            periphery_controller = PeripheryController(data['fwName'], data['fwVersion'], new_name, True)
            self.db_session.add(periphery_controller)
            self.db_session.commit()
            sensors = self.register_sensors(periphery_controller, data['sensors'])
            # save new id on controller
            self.redis_conn.publish(data['channel'], {'cmd': 'I'+str(periphery_controller._id), 'result_channel': None})
        else:
            # query database
            periphery_controller = self.db_session.query(PeripheryController).filter(PeripheryController._id==data['id']).first()
            periphery_controller.active = True
            self.db_session.commit()
        print('registered periphery controller: ' + periphery_controller.name)

    def register_sensors(self, periphery_controller, data):
        for s in data:
            sensor = Sensor(periphery_controller, s['name'], s['unit'], s['samplingTime'])
            self.db_session.add(sensor)
        self.db_session.commit()
    
    def remove_controller(self, data):
        periphery_controller = self.db_session.query(PeripheryController).filter(PeripheryController._id==data['id']).first()
        periphery_controller.active = False
        self.db_session.commit()
        print('removed periphery controller: ' + periphery_controller.name)
    
    def close(self):
        self.pubsub.close()


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s\n'
          '(example: "%s")' % (cmd, cmd))
    sys.exit(1)
    
def main(argv=sys.argv):
    if len(argv) > 1:
        usage(argv)
    worker = ControllerManager(redis_conn, db_session)
    try:
        worker.work()
    finally:
        worker.close()