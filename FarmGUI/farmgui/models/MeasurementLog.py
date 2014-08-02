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
    parameter_id = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    
    def __init__(self, parameter, time, value):
        self.parameter = parameter
        self.parameter_id = parameter._id
        self.time = time
        self.value = value
