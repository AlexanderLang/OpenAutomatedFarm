'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Boolean
from sqlalchemy.orm import relationship

from .meta import Base

class PeripheryController(Base):
    '''
    classdocs
    '''
    __tablename__ = 'PeripheryControllers'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    firmwareName = Column(Unicode(250), nullable=False)
    firmwareVersion = Column(Unicode(20), nullable=False)
    name = Column(Unicode(250), nullable=True, unique=True)
    active = Column(Boolean, nullable=False, default=False, unique=False)
    sensors = relationship("Sensor", order_by="Sensor._id", back_populates='controller')
    actuators = relationship("Actuator", order_by="Actuator._id", backref="controller")
    
    def __init__(self, fwName, fwVersion, name, active=True):
        self.firmwareName = fwName
        self.firmwareVersion = fwVersion
        self.name = name
        self.active = active
        

def init_PeripheryControllers(db_session):
    pass
