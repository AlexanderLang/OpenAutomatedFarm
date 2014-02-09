'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base

class Stage(Base):
	'''
	classdocs
	'''
	__tablename__ = 'Stages'

	_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	plantSettingId = Column(BigInteger, ForeignKey('PlantSettings._id'), nullable=False)
	number = Column(SmallInteger, nullable=False)
	duration = Column(SmallInteger, nullable=False)
	name = Column(Unicode(250), nullable=True)
	description = Column(Text, nullable=True)
	configurations = relationship("StageConfiguration", backref="Stages")


	def __init__(self, plantSetting, number, duration, name, description):
		'''
		Constructor
		'''
		self.plantSetting = plantSetting
		self.number = number
		self.duration = duration
		self.name = name
		self.description = description

