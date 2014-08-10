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

    def __init__(self, component, name, parameter_type, interval, sensor, description):
        """
        Constructor
        :type sensor: Sensor
        :type component: FarmComponent
        :type parameter_type: ParameterType
        """
        self.component = component
        self.component_id = component.id
        self.name = name
        self.parameter_type = parameter_type
        self.parameter_type_id = parameter_type.id
        self.interval = interval
        self.sensor = sensor
        if sensor is not None:
            self.sensor_id = sensor.id
        self.description = description

    @property
    def id(self):
        return self._id


def init_devices(db_session):
    pass
