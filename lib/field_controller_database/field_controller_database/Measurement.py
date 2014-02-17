'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy import ForeignKey

from .meta import Base

class Measurement(Base):
    '''
    classdocs
    '''
    __tablename__ = 'Measurements'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    measurandId = Column(SmallInteger, ForeignKey('Measurands._id'), nullable=False)
    sensorId = Column(Integer, ForeignKey('Sensors._id'), nullable=False)
    
    def __init__(self, parameter, sensor):
        self.parameter = parameter
        self.sensor = sensor
