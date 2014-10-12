from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep

import logging

from redis import Redis
from serial import SerialException
from pyramid.paster import get_appsettings

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import ParameterType
from ..models import PeripheryController
from ..models import Sensor
from ..models import Actuator
from ..models import DeviceType

from ..communication import SerialShell
from ..communication import get_redis_conn


class PeripheryControllerWorker(object):
    """
    classdocs
    """

    def __init__(self, devicename, redis, db_sm):
        self.redis_conn = redis
        self.db_sessionmaker = db_sm
        self.loop_time = timedelta(seconds=1)
        # connect with serial port
        self.serial = SerialShell(devicename)
        # register in database
        db_session = self.db_sessionmaker()
        self.controller_id = self.serial.get_id()
        if self.controller_id == 0:
            # new controller
            self.register_new_controller(db_session)
        else:
            # known controller (set active)
            periphery_controller = db_session.query(PeripheryController).filter_by(_id=self.controller_id).first()
            periphery_controller.active = True
        db_session.commit()
        # get sensor ids
        self.sensor_ids = []
        for sensor in periphery_controller.sensors:
            self.sensor_ids.append('s'+str(sensor.id))
        # get actuator ids
        self.actuator_ids = []
        for actuator in periphery_controller.actuators:
            self.actuator_ids.append('a'+str(actuator.id))
        # set up redis cache
        self.setup_redis_cache(periphery_controller)
        db_session.close()
        # let scheduler know the available sensors changed
        self.redis_conn.publish('periphery_controller_changes', 'connected id: '+str(self.controller_id))

    def register_new_controller(self, db_session):
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
        for i in range(len(sensors)):
            s = sensors[i]
            param_type = db_session.query(ParameterType).filter_by(unit=s['unit']).first()
            sensor = Sensor(periphery_controller, i, s['name'], param_type, s['precision'],
                            s['min'], s['max'])
            db_session.add(sensor)
        # register actuators
        actuators = self.serial.get_actuators()
        for i in range(len(actuators)):
            a = actuators[i]
            device_type = db_session.query(DeviceType).filter_by(unit=a['unit']).first()
            actuator = Actuator(periphery_controller, i, a['name'], device_type, a['default'])
            db_session.add(actuator)
        db_session.flush()

    def setup_redis_cache(self, pc):
        # publish sensor ids
        sensor_ids = []
        for s in pc.sensors:
            sensor_ids.append('s'+str(s.id))
        self.redis_conn.set('pc' + str(pc.id) + '.s', str(sensor_ids))
        # publish actuator ids
        actuator_ids = []
        for a in pc.actuators:
            actuator_ids.append('a' + str(a.id))
            self.redis_conn.set('a' + str(a.id) + '.default', str(a.default_value))
        self.redis_conn.set('pc' + str(pc.id) + '.a', str(actuator_ids))

    def get_actuator_value_from_redis(self, a_id):
        value = self.redis_conn.get(a_id)
        if value is None:
            return float(self.redis_conn.get(a_id + '.default'))
        return float(value)

    def publish_sensor_values(self):
        try:
            values = self.serial.get_sensor_values()
        except SerialException:
            self.close()
            exit()
        for i in range(len(self.sensor_ids)):
            self.redis_conn.setex(self.sensor_ids[i], values[i], 2*self.loop_time)

    def apply_actuator_values(self):
        values = []
        for i in range(len(self.actuator_ids)):
            values.append(self.get_actuator_value_from_redis(self.actuator_ids[i]))
        try:
            self.serial.set_actuator_values(values)
        except SerialException:
            self.close()
            exit()

    def work(self):
        last_run = datetime.now()
        while True:
            while datetime.now() - last_run < self.loop_time:
                sleep(0.05)
            last_run = datetime.now()
            self.publish_sensor_values()
            self.apply_actuator_values()

    def close(self):
        db_session = self.db_sessionmaker()
        periphery_controller = db_session.query(PeripheryController).filter_by(_id=self.controller_id).first()
        periphery_controller.active = False
        db_session.commit()
        db_session.close()
        # let scheduler know the available sensors changed
        self.redis_conn.publish('periphery_controller_changes', 'disconnected id: '+str(self.controller_id))


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
    redis_conn = get_redis_conn(config_uri)
    logging.basicConfig(filename=settings['log_directory'] + '/pc_' + dev_name.split('/')[-1] + '.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)

    worker = PeripheryControllerWorker(dev_name, redis_conn, db_sessionmaker)
    try:
        worker.work()
    finally:
        worker.close()