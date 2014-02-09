'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Time
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base

class StageConfiguration(Base):
	'''
	classdocs
	'''
	__tablename__ = 'StageConfigurations'

	_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	stageId = Column(BigInteger, ForeignKey('Stages._id'), nullable=False)
	parameterId = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
	parameter = relationship("Parameter")
	time = Column(Time, nullable=False)
	setpoint = Column(Float, nullable=False)
	upperLimit = Column(Float, nullable=False)
	lowerLimit = Column(Float, nullable=False)

	def __init__(self, parameter, time, setpoint, upperLimit, lowerLimit):
		'''
		Constructor
		'''
		self.parameter = parameter
		self.time = time
		self.setpoint = setpoint
		self.upperLimit = upperLimit
		self.lowerLimit = lowerLimit
		

def init_StageConfiguration():
	pass

