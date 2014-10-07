"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Boolean
from sqlalchemy.orm import relationship

from .meta import Base


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
                           back_populates='periphery_controller',
                           cascade='all, delete, delete-orphan')
    actuators = relationship("Actuator",
                             order_by="Actuator.index",
                             back_populates='periphery_controller',
                             cascade='all, delete, delete-orphan')

    def __init__(self, fw_name, fw_version, name, active=True):
        self.firmwareName = fw_name
        self.firmwareVersion = fw_version
        self.name = name
        self.active = active

    @property
    def id(self):
        return self._id
