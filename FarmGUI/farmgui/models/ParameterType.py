"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base


class ParameterType(Base):
    """
    classdocs
    """
    __tablename__ = 'ParameterTypes'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    unit = Column(Unicode(250), nullable=False)

    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable (dictionary) format"""
        ret_dict = {
            'id': self.id,
            'name': self.name,
            'unit': self.unit
        }
        return ret_dict

    def __repr__(self):
        return str(self.serialize)


def init_parameter_types(db_session):
    db_session.add(ParameterType('Temperature', '°C'))
    db_session.add(ParameterType('Humidity', '%'))
    db_session.add(ParameterType('Volume', 'Liter'))
    db_session.add(ParameterType('pH', 'pH'))
    db_session.add(ParameterType('Conductivity', 'mS'))
