"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base


class CalendarEntry(Base):
    """
    classdocs
    """
    __tablename__ = 'CalendarEntries'

    _id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    parameter_id = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
    entry_number = Column(SmallInteger, nullable=False)
    interpolation_id = Column(SmallInteger, ForeignKey('SetpointInterpolations._id'), nullable=False)
    interpolation = relationship('SetpointInterpolation')

    def __init__(self, parameter, entry_number, interpolation):
        self.parameter = parameter
        self.parameter_id = parameter.id
        self.entry_number = entry_number
        self.interpolation = interpolation
        self.interpolation_id = interpolation.id

    @property
    def id(self):
        return self._id
