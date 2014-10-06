"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base
from .meta import serialize


class Device(Base):
    """
    classdocs
    """

    __tablename__ = 'Devices'

    _id = Column(SmallInteger,
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    component_id = Column(SmallInteger,
                          ForeignKey('FarmComponents._id'),
                          nullable=False)
    component = relationship('FarmComponent', back_populates='devices')
    name = Column(Unicode(250),
                  nullable=False,
                  unique=False)
    device_type_id = Column(SmallInteger,
                               ForeignKey('DeviceTypes._id'),
                               nullable=False)
    device_type = relationship('DeviceType')
    description = Column(Text,
                         nullable=True)
    actuator_id = Column(SmallInteger,
                       ForeignKey('Actuators._id'),
                       nullable=True)
    actuator = relationship("Actuator")
    logs = relationship("DeviceLog", order_by="DeviceLog.time")

    def __init__(self, component, name, device_type, actuator, description):
        """
        Constructor
        :type component: FarmComponent
        """
        self.component = component
        self.component_id = component.id
        self.name = name
        self.device_type = device_type
        self.device_type_id = device_type.id
        self.actuator = actuator
        if actuator is not None:
            self.actuator_id = actuator.id
        self.description = description

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        return {
            '_id': self.id,
            'name': self.name,
            'description': self.description,
            'component': serialize(self.component),
            'device_type': serialize(self.device_type),
            'actuator': self.actuator.serialize
        }


def init_devices(db_session):
    pass
