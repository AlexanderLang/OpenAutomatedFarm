"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from farmgui.models import Base


class Display(Base):
    """
    classdocs
    """

    __tablename__ = 'Displays'

    _id = Column(SmallInteger,
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    display_type = Column(Unicode(250))
    name = Column(Unicode(250),
                  nullable=False,
                  unique=True)
    description = Column(Text,
                         nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'display',
        'polymorphic_on': display_type,
    }

    def __init__(self, name, description):
        """
        Constructor
        :type component: FarmComponent
        """
        self.name = name
        self.description = description

    @property
    def id(self):
        return self._id

    @property
    def serialize_display(self):
        """Return data in serializeable (dictionary) format"""
        ret_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        return ret_dict

    @property
    def serialize(self):
        return self.serialize_display

    def __repr__(self):
        return str(self.serialize)
