'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relationship

from .meta import Base

class PeripheryController(Base):
    '''
    classdocs
    '''
    __tablename__ = 'PeripheryControllers'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    serial = Column(Unicode(20), nullable=False)
    firmwareName = Column(Unicode(250), nullable=False)
    firmwareVersion = Column(Unicode(20), nullable=False)
    name = Column(Unicode(250))
    sensors = relationship("Sensor", backref="PeripheryControllers")
    actuators = relationship("Actuator", backref="PeripheryControllers")
    
    def __init__(self, serial, fwName, fwVersion):
        self.serial = serial
        self.firmwareName = fwName
        self.firmwareVersion = fwVersion
