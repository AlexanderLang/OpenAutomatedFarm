"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base


class RegulatorType(Base):
    """
    classdocs
    """
    __tablename__ = 'RegulatorTypes'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    description = Column(Unicode(250), nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @property
    def id(self):
        return self._id


def init_regulator_types(db_session):
    db_session.add(RegulatorType('P', 'P regulator'))
    db_session.add(RegulatorType('PI', 'PI regulator'))
