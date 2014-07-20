'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base

class Location(Base):
    '''
    classdocs
    '''
    __tablename__ = 'Locations'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    description = Column(Unicode(250), nullable=True)
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        

def init_Locations(db_session):
    db_session.add(Location('Plant Room', 'inside Air'))
    db_session.add(Location('Surroundings', 'outside Air'))
    db_session.add(Location('Root Room', 'Moist Air and water'))
    db_session.add(Location('Nutrient Tank', 'Water'))
    
