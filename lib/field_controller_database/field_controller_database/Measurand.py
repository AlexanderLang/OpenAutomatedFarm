'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text

from .meta import Base

class Measurand(Base):
	'''
	classdocs
	'''
	__tablename__ = 'Measurands'

	_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	name = Column(Unicode(250), nullable=True)
	unit = Column(Unicode(50), nullable=True)
	description = Column(Text, nullable=True)


	def __init__(self, name, unit, description):
		'''
		Constructor
		'''
		self.name = name
		self.unit = unit
		self.description = description
		

def init_Parameters(db_session):
	names = ["Air Temperature", "Water Temperature", "Air Humidity", "pH", "EC"]
	units = ["°C", "°C", "%", "", "mS"]
	descriptions = ["", "", "", "", ""]
	for i in range(len(names)):
		param = Parameter(names[i], units[i], descriptions[i])
		db_session.add(param)
