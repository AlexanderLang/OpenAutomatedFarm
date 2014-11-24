"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base


class DeviceLink(Base):
    """
    classdocs
    """
    __tablename__ = 'DeviceLinks'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    display_id = Column(SmallInteger, ForeignKey('Displays._id'), nullable=False)
    device_id = Column(SmallInteger, ForeignKey('Devices._id'), nullable=False)
    target = Column(Unicode(250), nullable=False)
    color = Column(Unicode(20), nullable=False)

    device = relationship('Device')

    def __init__(self, display, device, target, color):
        self.display = display
        self.device = device
        self.target = target
        self.color = color

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        return {'id': self._id,
                'display_id': self.display_id,
                'device_id': self.device_id,
                'target': self.target}

    def __repr__(self):
        return self.serialize
