"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from farmgui.models import Base


class DeviceType(Base):
    """
    classdocs
    """
    __tablename__ = 'DeviceTypes'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    unit = Column(Unicode(250), nullable=False)

    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

    @property
    def id(self):
        return self._id


def init_device_types(db_session):
    db_session.add(DeviceType('Linear', '%'))
    db_session.add(DeviceType('ON/OFF', '1/0'))