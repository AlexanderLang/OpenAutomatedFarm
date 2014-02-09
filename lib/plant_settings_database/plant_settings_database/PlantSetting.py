'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base

class PlantSetting(Base):
	'''
	classdocs
	'''
	__tablename__ = 'PlantSettings'

	_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	plant = Column(Unicode(250), nullable=False)
	variety = Column(Unicode(250), nullable=False)
	method = Column(Unicode(250), nullable=False)
	description = Column(Text, nullable=True)
	stages = relationship("Stage", backref="PlantSettings")


	def __init__(self, plant, variety, method, description):
		'''
		Constructor
		'''
		self.plant = plant
		self.variety = variety
		self.method = method
		self.description = description

