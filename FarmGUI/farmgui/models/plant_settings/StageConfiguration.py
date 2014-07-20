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
from .PlantSetting import PlantSetting
from .Stage import Stage
from .Parameter import Parameter

import datetime

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

	def __init__(self, stage, parameter, time, setpoint, upperLimit, lowerLimit):
		'''
		Constructor
		'''
		self.stage = stage
		self.parameter = parameter
		self.time = time
		self.setpoint = setpoint
		self.upperLimit = upperLimit
		self.lowerLimit = lowerLimit
		

def init_StageConfigurations(db_session):
	plantSetting = db_session.query(PlantSetting).filter(PlantSetting.plant=='tomato').first()
	stage = db_session.query(Stage).filter(Stage.plantSettingId==plantSetting._id).filter(Stage.name=='groth').first()

	parameter = db_session.query(Parameter).filter(Parameter.name=='Blue Light').first()
	db_session.add(StageConfiguration(stage, parameter, datetime.time(0,0), 0, 1, 0))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(6,0), 0, 1, 0))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(6,30), 100, 100, 90))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(23,30), 100, 100, 90))

	parameter = db_session.query(Parameter).filter(Parameter.name=='Red Light').first()
	db_session.add(StageConfiguration(stage, parameter, datetime.time(0,1), 0, 1, 0))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(6,1), 0, 1, 0))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(6,31), 99, 100, 90))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(23,31), 99, 100, 90))

	parameter = db_session.query(Parameter).filter(Parameter.name=='White Light').first()
	db_session.add(StageConfiguration(stage, parameter, datetime.time(0,2), 0, 1, 0))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(6,2), 0, 1, 0))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(6,32), 98, 100, 90))
	db_session.add(StageConfiguration(stage, parameter, datetime.time(23,32), 98, 100, 90))

