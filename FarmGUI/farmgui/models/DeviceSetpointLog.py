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


class DeviceSetpointLog(Base):
    """
    classdocs
    """
    __tablename__ = 'DeviceSetpointLogs'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    device_id = Column(SmallInteger, ForeignKey('Devices._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    setpoint = Column(Float, nullable=True)

    def __init__(self, device, time, setpoint):
        self.device = device
        self.time = time
        self.setpoint = setpoint

    @property
    def id(self):
        return self._id
