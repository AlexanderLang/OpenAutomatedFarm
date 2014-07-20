'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey

from .meta import Base

class MeasurementLog(Base):
    '''
    classdocs
    '''
    __tablename__ = 'MeasurementLogs'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    measurementId = Column(SmallInteger, ForeignKey('Measurements._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    
    def __init__(self, measurement, time, value):
        self.measurement = measurement
        self.measurementId = measurement._id
        self.time = time
        self.value = value
    
    def __str__(self):
        name = self.measurement.location.name + ': '
        name = name + self.measurement.parameter.name + ' = '
        name = name + str(self.value) + ' [' + self.measurement.parameter.unit + ']'
        return name
