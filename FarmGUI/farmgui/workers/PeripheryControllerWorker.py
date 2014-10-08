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

redis_conn = Redis('localhost', 6379)
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from ..models import Base
from ..models import ParameterType
from ..models import PeripheryController
from ..models import Sensor
from ..models import Actuator
from ..models import DeviceType

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
            self.register_new_controller(db_session)
        else:
            # known controller (set active)
            self.periphery_controller = db_session.query(PeripheryController).filter_by(_id=self.controller_id).first()
            self.periphery_controller.active = True
        db_session.commit()
        db_session.close()
        # get sensor ids
        self.sensor_ids = []
        db_session = self.db_sessionmaker()
        sensors = db_session.query(Sensor).filter_by(periphery_controller_id=self.controller_id).all()
        for sensor in sensors:
            self.sensor_ids.append('s'+str(sensor.id))
        # get actuator ids
        self.actuator_ids = []
        actuators = db_session.query(Actuator).filter_by(periphery_controller_id=self.controller_id).all()
        for actuator in actuators:
            self.actuator_ids.append('a'+str(actuator.id))
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
            db_session.flush()
            # create redis entry
            self.redis_conn.set('s' + str(sensor.id), '0')
        # register actuators
        actuators = self.serial.get_actuators()
        for i in range(len(actuators)):
            a = actuators[i]
            device_type = db_session.query(DeviceType).filter_by(unit=a['unit']).first()
            actuator = Actuator(periphery_controller, i, a['name'], device_type, a['default'])
            db_session.add(actuator)
            db_session.flush()
            # create redis entry
            self.redis_conn.set('a' + str(actuator.id), '0')

    def publish_sensor_values(self):
        try:
            values = self.serial.get_sensor_values()
        except SerialException:
            self.close()
            exit()
        for i in range(len(self.sensor_ids)):
            self.redis_conn.set(self.sensor_ids[i], values[i])

    def apply_actuator_values(self):
        values = []
        for i in range(len(self.actuator_ids)):
            values.append(self.redis_conn.get(self.actuator_ids[i]))
        try:
            self.serial.set_actuator_values(values)
        except SerialException:
            self.close()
            exit()




    def work(self):
        loop_time = 1
        while True:
            self.publish_sensor_values()
            self.apply_actuator_values()
            sleep(loop_time)

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
    logging.basicConfig(filename=settings['log_directory'] + '/pc_' + dev_name.split('/')[-1] + '.log',
                        format='%(levelname)s:%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG)

    worker = PeripheryControllerWorker(dev_name, redis_conn, db_sessionmaker)
    try:
        worker.work()
    finally:
        worker.close()