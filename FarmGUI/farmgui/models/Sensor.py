"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship

from .meta import Base


class Sensor(Base):
    """
    classdocs
    """
    __tablename__ = 'Sensors'

    _id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    periphery_controller_id = Column(SmallInteger, ForeignKey('PeripheryControllers._id'), nullable=False)
    periphery_controller = relationship('PeripheryController', back_populates='sensors')
    name = Column(Unicode(250), nullable=False)
    parameter_type_id = Column(SmallInteger, ForeignKey('ParameterTypes._id'), nullable=False)
    parameter_type = relationship('ParameterType')
    precision = Column(Float(), nullable=False)
    sampling_time = Column(Float(), nullable=False)
    minimum = Column(Float(), nullable=False)
    maximum = Column(Float(), nullable=False)

    def __init__(self, periphery_controller, name, parameter_type, precision, sampling_time, min, max):
        self.peripheryController = periphery_controller
        self.periphery_controller_id = periphery_controller.id
        self.name = name
        self.parameter_type = parameter_type
        self.parameter_type_id = parameter_type.id
        self.precision = precision
        self.sampling_time = sampling_time
        self.minimum = min
        self.maximum = max

    @property
    def id(self):
        return self._id
