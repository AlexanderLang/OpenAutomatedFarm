"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey

from .meta import Base


class DeviceLog(Base):
    """
    classdocs
    """
    __tablename__ = 'DeviceLogs'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    device_id = Column(SmallInteger, ForeignKey('Devices._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)

    def __init__(self, device, time, value):
        self.device = device
        self.device_id = device.id
        self.time = time
        self.value = value
