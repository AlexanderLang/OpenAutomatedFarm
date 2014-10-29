"""
Created on Feb 15, 2014

@author: alex
"""

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base


class FieldSetting(Base):
    """
    classdocs
    """
    __tablename__ = 'FieldSettings'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    value = Column(Unicode(250), nullable=True)
    description = Column(Unicode(250), nullable=True)

    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

    @staticmethod
    def get_cultivation_start(db_session):
        time_str = db_session.query(FieldSetting).filter_by(name='cultivation_start').first().value
        return datetime.strptime(time_str, "%Y-%m-%d")


def init_field_settings(db_session):
    db_session.add(FieldSetting('cultivating_plant', 'tomato', 'the plant being grown in the field right now'))
    db_session.add(FieldSetting('cultivation_start', str(datetime.today().date()), 'start date'))
