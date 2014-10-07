"""
Created on Feb 15, 2014

@author: alex
"""
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship

from .meta import Base
from .meta import serialize


class Sensor(Base):
    """
    classdocs
    """
    __tablename__ = 'Sensors'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    periphery_controller_id = Column(SmallInteger, ForeignKey('PeripheryControllers._id'), nullable=False)
    periphery_controller = relationship('PeripheryController', back_populates='sensors')
    index = Column(SmallInteger, nullable=False)
    name = Column(Unicode(250), nullable=False)
    parameter_type_id = Column(SmallInteger, ForeignKey('ParameterTypes._id'), nullable=False)
    parameter_type = relationship('ParameterType')
    precision = Column(Float(), nullable=False)
    minimum = Column(Float(), nullable=False)
    maximum = Column(Float(), nullable=False)

    def __init__(self, periphery_controller, index, name, parameter_type, precision, minimum, maximum):
        self.peripheryController = periphery_controller
        self.periphery_controller_id = periphery_controller.id
        self.index = index
        self.name = name
        self.parameter_type = parameter_type
        self.parameter_type_id = parameter_type.id
        self.precision = precision
        self.minimum = minimum
        self.maximum = maximum
        self.last_measured = datetime.now()


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
            'parameter_type': serialize(self.parameter_type),
            'precision': self.precision,
            'minimum': self.minimum,
            'maximum': self.maximum
        }
