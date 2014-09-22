"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base
from .meta import serialize


class Actuator(Base):
    """
    classdocs
    """
    __tablename__ = 'Actuators'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    periphery_controller_id = Column(SmallInteger, ForeignKey('PeripheryControllers._id'), nullable=False)
    periphery_controller = relationship('PeripheryController', back_populates='actuators')
    name = Column(Unicode(250), nullable=False)
    device_type_id = Column(SmallInteger,
                               ForeignKey('DeviceTypes._id'),
                               nullable=False)
    device_type = relationship('DeviceType')

    def __init__(self, periphery_controller, name, device_type):
        self.peripheryController = periphery_controller
        self.periphery_controller_id = periphery_controller.id
        self.name = name
        self.device_type = device_type
        self.device_type_id = device_type.id

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        return {
            '_id': self.id,
            'periphery_controller': serialize(self.periphery_controller),
            'name': self.name,
            'device_type': serialize(self.device_type)
        }
