from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime

from redis import Redis
from pyramid.paster import get_appsettings

redis_conn = Redis('localhost', 6379)
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import ParameterType
from ..models import PeripheryController
from ..models import Sensor
from ..models import Actuator
from ..models import DeviceType

db_engine = None
db_sessionmaker = None

from ..communication import SerialShell


class PeripheryControllerWorker(object):
    """
    classdocs
    """

    def __init__(self, devicename, redis, db_sm):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        # connect with serial port
        self.serial = SerialShell(devicename)
        # register in database
        db_session = self.db_sessionmaker()
        self.controller_id = self.serial.get_id()
        if self.controller_id == 0:
            # new controller
            fw_name = self.serial.get_firmware_name()
            fw_version = self.serial.get_firmware_version()
            new_name = 'new ' + fw_name + ' (version ' + fw_version + ')'
            periphery_controller = PeripheryController(fw_name, fw_version, new_name, True)
            db_session.add(periphery_controller)
            db_session.flush()
            # save new id on controller
            self.controller_id = periphery_controller.id
            self.serial.set_id(self.controller_id)
            # register sensors
            sensors = self.serial.get_sensors()
            for s in sensors:
                param_type = db_session.query(ParameterType).filter_by(unit=s['unit']).first()
                sensor = Sensor(periphery_controller, s['name'], param_type, s['precision'],
                                s['samplingTime'], s['min'], s['max'])
                db_session.add(sensor)
            # register actuators
            actuators = self.serial.get_actuators()
            for a in actuators:
                device_type = db_session.query(DeviceType).filter_by(unit=a['unit']).first()
                actuator = Actuator(periphery_controller, a['name'], device_type)
                db_session.add(actuator)
        else:
            # known controller (set active)
            periphery_controller = db_session.query(PeripheryController).filter_by(_id=self.controller_id).first()
            periphery_controller.active = True
        db_session.commit()
        db_session.close()
        # create command queue
        self.channel_name = 'periphery_controller_' + str(self.controller_id)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(self.channel_name)
        # let scheduler know the available sensors changed
        self.redis_conn.publish('periphery_controller_changes', 'connected id: '+str(self.controller_id))

    def work(self):
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                # print('got data: ' + str(data))
                result = self.serial.execute_cmd(data['cmd'])
                if data['result_channel'] is not None:
                    response = {'caller_id': data['caller_id'],
                                'time': str(datetime.now()),
                                'value': result}
                    self.redis_conn.publish(data['result_channel'], response)
                    print('oaf_cw: ' + data['result_channel'] + '(' + data['cmd'] + ': ' + result + ')')

    def close(self):
        db_session = self.db_sessionmaker()
        periphery_controller = db_session.query(PeripheryController).filter_by(_id=self.controller_id).first()
        periphery_controller.active = False
        db_session.commit()
        db_session.close()
        # let scheduler know the available sensors changed
        self.redis_conn.publish('periphery_controller_changes', 'disconnected id: '+str(self.controller_id))
        self.pubsub.close()


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <dev_name>\n'
          '(example: "%s development.ini /dev/ttyACM0")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 3:
        usage(argv)
    config_uri = argv[1]
    dev_name = argv[2]

    settings = get_appsettings(config_uri)
    db_engine = engine_from_config(settings, 'sqlalchemy.')
    db_sessionmaker = sessionmaker(bind=db_engine)
    Base.metadata.bind = db_engine

    worker = PeripheryControllerWorker(dev_name, redis_conn, db_sessionmaker)
    try:
        worker.work()
    finally:
        worker.close()