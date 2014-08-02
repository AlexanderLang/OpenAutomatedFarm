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
    unit = Column(Unicode(50), nullable=False)
    sampling_time = Column(Float(), nullable=False)

    def __init__(self, periphery_controller, name, unit, sampling_time):
        self.peripheryController = periphery_controller
        self.periphery_controller_id = periphery_controller.id
        self.name = name
        self.unit = unit
        self.sampling_time = sampling_time

    @property
    def id(self):
        return self._id
