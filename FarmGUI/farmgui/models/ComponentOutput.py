"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relationship

from farmgui.models import Base


class ComponentOutput(Base):
    """
    classdocs
    """
    __tablename__ = 'ComponentOutputs'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    component_id = Column(SmallInteger, ForeignKey('Components._id'))
    name = Column(Unicode(250), nullable=False)

    def __init__(self, component, name):
        self.component = component
        self.name = name

    @property
    def id(self):
        return self._id

    @property
    def redis_key(self):
        return 'c'+str(self._id)
