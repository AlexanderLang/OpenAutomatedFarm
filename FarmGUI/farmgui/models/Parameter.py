'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base

class Parameter(Base):
	'''
	classdocs
	'''
	__tablename__ = 'Parameters'

	_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	component_id = Column(SmallInteger, ForeignKey('FarmComponents._id'), nullable=False)
	component = relationship('FarmComponent', back_populates='parameters')
	name = Column(Unicode(250), nullable=False, unique=True)
	parameter_type_id = Column(SmallInteger, ForeignKey('ParameterTypes._id'), nullable=False)
	parameter_type = relationship('ParameterType')
	description = Column(Text, nullable=True)
	interval = Column(Float(), nullable=False)
	sensor_id = Column(Integer, ForeignKey('Sensors._id'), nullable=True)
	sensor = relationship("Sensor", backref="measurement")
	logs = relationship("MeasurementLog", order_by="MeasurementLog.time")


	def __init__(self, component, name, parameter_type, interval, sensor, description):
		'''
		Constructor
		'''
		self.component = component
		self.component_id = component._id
		self.name = name
		self.parameter_type = parameter_type
		self.parameter_type_id = parameter_type._id
		self.interval = interval
		self.sensor = sensor
		if sensor is not None:
			self.sensor_id = sensor._id
		self.description = description
		

def init_Parameters(db_session):
	pass
