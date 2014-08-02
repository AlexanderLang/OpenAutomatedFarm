'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relationship

from .meta import Base

class FarmComponent(Base):
    '''
    classdocs
    '''
    __tablename__ = 'FarmComponents'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    description = Column(Unicode(250), nullable=True)
    parameters = relationship("Parameter", order_by="Parameter.name", back_populates='component', cascade='all, delete, delete-orphan')
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        

def init_FarmComponents(db_session):
    db_session.add(FarmComponent('Plant Room', 'inside Air'))
    db_session.add(FarmComponent('Root Room', 'Moist Air and water'))
    db_session.add(FarmComponent('Nutrient Tank', 'Water'))
    
