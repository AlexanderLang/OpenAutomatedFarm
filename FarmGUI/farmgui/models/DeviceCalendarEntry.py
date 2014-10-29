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


class DeviceCalendarEntry(Base):
    """
    classdocs
    """
    __tablename__ = 'DeviceCalendarEntries'

    _id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    device_id = Column(SmallInteger, ForeignKey('Devices._id'), nullable=False)
    entry_number = Column(SmallInteger, nullable=False)
    interpolation_id = Column(SmallInteger, ForeignKey('SetpointInterpolations._id'), nullable=False)
    interpolation = relationship('SetpointInterpolation')

    def __init__(self, device, entry_number, interpolation):
        self.device = device
        self.device_id = device.id
        self.entry_number = entry_number
        self.interpolation = interpolation
        self.interpolation_id = interpolation.id
        self.end_time = None

    @property
    def id(self):
        return self._id

    def get_value_at(self, time):
        interpolation_time = (time - self.end_time).total_seconds() + self.interpolation.end_time
        return self.interpolation.get_value_at(interpolation_time)
