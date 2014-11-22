"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from .meta import Base


class ParameterLink(Base):
    """
    classdocs
    """
    __tablename__ = 'ParameterLinks'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    display_id = Column(SmallInteger, ForeignKey('Displays._id'), nullable=False)
    parameter_id = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
    target = Column(Unicode(250), nullable=False)

    parameter = relationship('Parameter')

    def __init__(self, display, parameter, target):
        self.display = display
        self.parameter = parameter
        self.target = target

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        return {'id': self._id,
                'display_id': self.display_id,
                'parameter_id': self.parameter_id,
                'target': self.target}

    def __repr__(self):
        return self.serialize
