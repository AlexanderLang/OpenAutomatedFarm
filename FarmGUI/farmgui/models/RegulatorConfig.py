"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base


class RegulatorConfig(Base):
    """
    classdocs
    """
    __tablename__ = 'RegulatorConfigs'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    regulator_id = Column(SmallInteger, ForeignKey('Regulators._id'))
    name = Column(Unicode(250), nullable=False)
    value = Column(Unicode(250), nullable=False)
    description = Column(Unicode(250), nullable=False)

    def __init__(self, regulator, name, value, description):
        self.regulator = regulator
        self.regulator_id = regulator.id
        self.name = name
        self.value = value
        self.description = description

    @property
    def id(self):
        return self._id


def init_regulator_config(db_session):
    pass
