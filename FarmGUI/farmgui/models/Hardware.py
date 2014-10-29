"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text

from farmgui.models import Base


class Hardware(Base):
    """
    classdocs
    """

    __tablename__ = 'Hardware'

    _id = Column(SmallInteger,
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    hardware_type = Column(Unicode(250))
    periphery_controller_id = Column(SmallInteger, ForeignKey('PeripheryControllers._id'), nullable=False)
    index = Column(SmallInteger, nullable=False)
    name = Column(Unicode(250),
                  nullable=False,
                  unique=False)
    description = Column(Text,
                         nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'hardware',
        'polymorphic_on': hardware_type,
    }

    def __init__(self, preiphery_controller, index, name, description):
        """
        Constructor
        :type component: FarmComponent
        """
        self.periphery_controller = preiphery_controller
        self.index = index
        self.name = name
        self.description = description

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable (dictionary) format"""
        return {
            '_id': self.id,
            'name': self.name,
            'description': self.description
        }
