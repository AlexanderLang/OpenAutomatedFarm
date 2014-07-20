'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from .meta import Base
from .Location import Location
from .Measurand import Measurand
from .PeripheryController import PeripheryController
from .Sensor import Sensor

class Measurement(Base):
	'''
	classdocs
	'''
	__tablename__ = 'Measurements'

	_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	locationId = Column(SmallInteger, ForeignKey('Locations._id'), nullable=False)
	location = relationship('Location')
	measurandId = Column(SmallInteger, ForeignKey('Measurands._id'), nullable=False)
	measurand = relationship('Measurand')
	sensorId = Column(Integer, ForeignKey('Sensors._id'), nullable=True)
	sensor = relationship("Sensor", backref="measurement")
	interval = Column(Float(), nullable=False)
	description = Column(Text, nullable=True)
	logs = relationship("MeasurementLog", order_by="MeasurementLog.time")


	def __init__(self, location, measurand, sensor, interval, description):
		'''
		Constructor
		'''
		self.location = location
		self.locationId = location._id
		self.measurand = measurand
		self.measurandId = measurand._id
		self.sensor = sensor
		self.sensorId = sensor._id
		self.interval = interval
		self.description = description
	
	def __str__(self):
		return '{ ' + self.location.name + ': ' + self.measurand.name + ' }'
		

def init_Measurements(db_session):
	pass
