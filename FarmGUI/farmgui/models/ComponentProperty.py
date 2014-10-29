"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from farmgui.models import Base


class ComponentProperty(Base):
    """
    classdocs
    """
    __tablename__ = 'ComponentProperties'

    _id = Column(SmallInteger,
                 primary_key=True, autoincrement=True, nullable=False, unique=True)
    component_id = Column(SmallInteger, ForeignKey('Components._id'))
    name = Column(Unicode(250), nullable=False)
    value = Column(Unicode(250), nullable=False)

    def __init__(self, component, name, value):
        """

        :param component:
        :param name:
        :param value:
        """
        self.component = component
        self.name = name
        self.value = value

    @property
    def id(self):
        return self._id

