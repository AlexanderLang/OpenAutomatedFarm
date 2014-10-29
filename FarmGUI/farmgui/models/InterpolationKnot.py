"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey

from farmgui.models import Base


class InterpolationKnot(Base):
    """
    classdocs
    """
    __tablename__ = 'InterpolationKnots'

    _id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    interpolation_id = Column(SmallInteger, ForeignKey('SetpointInterpolations._id'), nullable=False)
    time = Column(Float, nullable=False)
    value = Column(Float, nullable=False)

    def __init__(self, interpolation, time, value):
        self.interpolation = interpolation
        self.time = time
        self.value = value

    @property
    def id(self):
        return self._id
