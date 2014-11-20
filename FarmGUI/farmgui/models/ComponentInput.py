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
    connected_output_id = Column(SmallInteger, ForeignKey('ComponentOutputs._id'), nullable=True)
    connected_output = relationship("ComponentOutput")

    def __init__(self, component, name, connected_output=None):
        self.component = component
        self.name = name
        self.connected_output = connected_output

    @property
    def id(self):
        return self._id

    @property
    def redis_key(self):
        if self.connected_output is not None:
            return self.connected_output.redis_key
        return 'nc_' + str(self._id)

    @property
    def serialize(self):
        """Return data in serializeable format"""
        ret_dict = {'id': self._id,
                    'name': self.name,
                    'connected_output': None,
                    'redis_key': self.redis_key}
        if self.connected_output is not None:
            ret_dict['connected_output'] = self.connected_output.serialize
        return ret_dict

    def __repr__(self):
        return str(self.serialize)
