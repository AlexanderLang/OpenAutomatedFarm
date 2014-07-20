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
redis_conn = Redis('localhost', 6379)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.field_controller import Base as Field_Controller_Base
from ..models.field_controller import PeripheryController
from ..models.field_controller import Sensor
from ..models.field_controller import Measurement
from ..models.field_controller import MeasurementLog

db_engine = create_engine('mysql+mysqlconnector://oaf:oaf_password@localhost/FieldController')
db_sessionmaker = sessionmaker(bind=db_engine)
Field_Controller_Base.metadata.bind = db_engine

class MeasurementScheduler(object):
    '''
    classdocs
    '''
    
    def __init__(self, db_sessionmaker, redis_conn):
        self.redis_conn = redis_conn
        self.db_sessionmaker = db_sessionmaker
        # listen for changes in measurements (and controller connections)
        self.pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('measurement_changes', 'log_measurements')
        self.schedule = {}
        self.db_session = self.db_sessionmaker()
        self.recalculate_schedule()
    
    def work(self):
        # main loop
        while True:
            # listen for messages
            message = self.pubsub.get_message()
            if message is not None:
                print('got message: '+str(message))
                if message['channel'] == b'measurement_changes':
                    # something changed
                    self.db_session.close()
                    self.db_session = self.db_sessionmaker()
                    self.recalculate_schedule()
                if message['channel'] == b'log_measurements':
                    data = eval(message['data'])
                    m = self.db_session.query(Measurement).filter(Measurement._id == data['caller_id']).first()
                    log = MeasurementLog(m, data['time'], data['value'])
                    self.db_session.add(log)
                    self.db_session.commit()
            # get time
            now = datetime.now()
            #print(str(now)+':')
            for m in self.schedule:
                if self.schedule[m] < now:
                    # execute
                    self.execute_measurement(m)
                    self.schedule[m] = now + timedelta(seconds=m.interval)
            sleep(0.5)
            
                
    
    def execute_measurement(self, m):
        channel_name = 'periphery_controller_'+str(m.sensor.peripheryControllerId)
        data = {}
        data['cmd'] = 's'+m.sensor.name
        data['result_channel'] = 'log_measurements'
        data['caller_id'] = m._id
        self.redis_conn.publish(channel_name, data)
        #print('oaf_ms: measure ' + str(m))
    
    def recalculate_schedule(self):
        logging.info('recalculating schedule')
        new_schedule = {}
        # get active controllers
        controllers = self.db_session.query(PeripheryController).filter(PeripheryController.active == True).all()
        # get ids of present sensors
        sensor_ids = []
        for controller in controllers:
            for sensor in controller.sensors:
                sensor_ids.append(sensor._id)
        if len(sensor_ids) > 0:
            # get measurements with present sensors
            measurements = self.db_session.query(Measurement).filter(Measurement.sensorId.in_(sensor_ids))
            # schedule measurements
            for m in measurements:
                new_schedule[m] = datetime.now() + timedelta(seconds=m.interval)
                logging.info('every '+str(m.interval)+' seconds measure: '+m.measurand.name+' of '+m.location.name)
        else:
            logging.info('no measurements to schedule')
        self.schedule = new_schedule
        
        


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s\n'
          '(example: "%s")' % (cmd, cmd))
    sys.exit(1)
    
def main(argv=sys.argv):
    if len(argv) > 1:
        usage(argv)
    worker = MeasurementScheduler(db_sessionmaker, redis_conn)
    worker.work()
    