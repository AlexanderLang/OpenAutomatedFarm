"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Boolean
from sqlalchemy.orm import relationship

from farmgui.models import Base
from farmgui.models import init_sensors
from farmgui.models import init_actuators


class PeripheryController(Base):
    """
    classdocs
    """
    __tablename__ = 'PeripheryControllers'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    firmwareName = Column(Unicode(250), nullable=False)
    firmwareVersion = Column(Unicode(20), nullable=False)
    name = Column(Unicode(250), nullable=True, unique=True)
    active = Column(Boolean, nullable=False, default=False, unique=False)
    sensors = relationship("Sensor",
                           order_by="Sensor.index",
                           backref='periphery_controller',
                           cascade='all, delete-orphan')
    actuators = relationship("Actuator",
                             order_by="Actuator.index",
                             backref='periphery_controller',
                             cascade='all, delete-orphan')

    def __init__(self, fw_name, fw_version, name, active=False):
        self.firmwareName = fw_name
        self.firmwareVersion = fw_version
        self.name = name
        self.active = active

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable (dictionary) format"""
        ret_dict = {
            'id': self.id,
            'name': self.name,
            'firmwareName': self.firmwareName,
            'firmwareVersion': self.firmwareVersion,
            'active': self.active
        }
        sensors = []
        for s in self.sensors:
            sensors.append(s.serialize)
        ret_dict['sensors'] = sensors
        actuators = []
        for a in self.actuators:
            actuators.append(a.serialize)
        ret_dict['actuators'] = actuators
        return ret_dict


def init_periphery_controllers(db_session):
    pc = PeripheryController('Dummy', '0.1', 'Dummy')
    db_session.add(pc)
    init_sensors(db_session, pc)
    init_actuators(db_session, pc)