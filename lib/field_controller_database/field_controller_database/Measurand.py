'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base

class Measurand(Base):
    '''
    classdocs
    '''
    __tablename__ = 'Measurands'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    unit = Column(Unicode(100), nullable=False)
    description = Column(Unicode(250), nullable=True)
    
    def __init__(self, name, unit, description):
        self.name = name
        self.unit = unit
        self.description = description
        

def init_Measurands(db_session):
    db_session.add(Measurand('Air Temperature', '°C', None))
    db_session.add(Measurand('Air Humidity', '%', None))
    db_session.add(Measurand('Water Temperature', '°C', None))
    db_session.add(Measurand('Water pH', '1', None))
    db_session.add(Measurand('Water EC', 'mS', None))
    
"Air Temperature", "Water Temperature", "Air Humidity", "pH", "EC", "Blue Light", "Red Light", "White Light"