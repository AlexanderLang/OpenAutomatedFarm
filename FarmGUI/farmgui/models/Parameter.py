'''
Created on Nov 17, 2013

@author: alex
'''

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy.types import Text

from .meta import Base

class Parameter(Base):
	'''
	classdocs
	'''
	__tablename__ = 'Parameters'

	_id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
	name = Column(Unicode(250), nullable=False, unique=True)
	unit = Column(Unicode(50), nullable=False)
	lower_limit = Column(Float, nullable=False)
	upper_limit = Column(Float, nullable=False)
	description = Column(Text, nullable=True)


	def __init__(self, name, unit, lower_limit, upper_limit, description):
		'''
		Constructor
		'''
		self.name = name
		self.unit = unit
		self.lower_limit = lower_limit
		self.upper_limit = upper_limit
		self.description = description
		

def init_Parameters(db_session):
	names = ["Air Temperature", "Water Temperature", "Air Humidity", "pH", "EC", "Blue Light", "Red Light", "White Light"]
	units = ["°C", "°C", "%", "", "mS", "%", "%", "%"]
	_min =   [0,     0,    5,   0,  0, 0, 0, 0]
	_max =   [40,    40,   100, 14, 5000, 100, 100, 100]
	descriptions = ["", "", "", "", "", "", "", ""]
	for i in range(len(names)):
		param = Parameter(names[i], units[i], _min[i], _max[i], descriptions[i])
		db_session.add(param)
