'''
Created on Feb 15, 2014

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Float
from sqlalchemy.types import Unicode
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base

class Actuator(Base):
    '''
    classdocs
    '''
    __tablename__ = 'Actuators'

    _id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    periphery_controller_id = Column(SmallInteger, ForeignKey('PeripheryControllers._id'), nullable=False)
    periphery_controller = relationship('PeripheryController', back_populates='actuators')
    name = Column(Unicode(250), nullable=False)
    setPoint = Column(Float, nullable=False)
    
    def __init__(self, periphery_controller, name, setPoint):
        self.peripheryController = periphery_controller
        self.periphery_controller_id = periphery_controller._id
        self.name = name
        self.setPoint = setPoint
