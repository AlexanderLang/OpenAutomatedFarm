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


class ComponentInput(Base):
    """
    classdocs
    """
    __tablename__ = 'ComponentInputs'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    component_id = Column(SmallInteger, ForeignKey('Components._id'))
    name = Column(Unicode(250), nullable=False)
    output_id = Column(SmallInteger, ForeignKey('ComponentOutputs._id'), nullable=True)
    connected_output = relationship("ComponentOutput")

    def __init__(self, component, name, connected_output=None):
        self.component = component
        self.name = name
        self.connected_output = connected_output

    @property
    def id(self):
        return self._id
