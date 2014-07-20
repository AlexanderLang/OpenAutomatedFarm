'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base

class Sensor(Base):
    '''
    classdocs
    '''
    __tablename__ = 'Sensors'

    _id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    peripheryControllerId = Column(SmallInteger, ForeignKey('PeripheryControllers._id'), nullable=False)
    controller = relationship('PeripheryController', back_populates='sensors')
    name = Column(Unicode(250), nullable=False)
    unit = Column(Unicode(50), nullable=False)
    samplingTime = Column(Float(), nullable=False)
    
    
    def __init__(self, peripheryController, name, unit, samplingTime):
        self.peripheryController = peripheryController
        self.peripheryControllerId = peripheryController._id
        self.name = name
        self.unit = unit
        self.samplingTime = samplingTime
