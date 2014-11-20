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


class Component(Base):
    """
    classdocs
    """

    __tablename__ = 'Components'

    _id = Column(SmallInteger,
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    component_type = Column(Unicode(250))
    name = Column(Unicode(250),
                  nullable=False,
                  unique=False)
    description = Column(Text,
                         nullable=True)
    _inputs = relationship('ComponentInput',
                           collection_class=attribute_mapped_collection('name'),
                           backref="component",
                           cascade="all, delete, delete-orphan")
    _outputs = relationship('ComponentOutput',
                            collection_class=attribute_mapped_collection('name'),
                            backref="component",
                            cascade="all, delete, delete-orphan")
    _properties = relationship('ComponentProperty',
                               collection_class=attribute_mapped_collection('name'),
                               backref="component",
                               cascade="all, delete, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'component',
        'polymorphic_on': component_type,
    }

    _order = None

    def __init__(self, name, description):
        """
        Constructor
        :type component: FarmComponent
        """
        self.name = name
        self.description = description

    def connect_input(self, input_name, output):
        #print('before conn: ' + str(self._inputs))
        inp = self._inputs[input_name]
        inp.connected_output = output
        #print('after conn: ' + str(self._inputs))

    @property
    def id(self):
        return self._id

    @property
    def order(self):
        if self._order is None:
            order = -1
            for in_key in self._inputs:
                inp = self._inputs[in_key]
                if inp.connected_output is not None:
                    output_comp = inp.connected_output.component
                    if output_comp.order > order:
                        order = output_comp.order
            self._order = order + 1
        return self._order

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def properties(self):
        return self._properties

    @property
    def serialize_component(self):
        """Return data in serializeable (dictionary) format"""
        ret_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        inputs = {}
        for key in self._inputs:
            inputs[key] = self._inputs[key].serialize
        ret_dict['inputs'] = inputs
        outputs = {}
        for key in self._outputs:
            outputs[key] = self._outputs[key].serialize
        ret_dict['outputs'] = outputs
        properties = {}
        for key in self._properties:
            properties[key] = self._properties[key].serialize
        ret_dict['properties'] = properties
        return ret_dict

    @property
    def serialize(self):
        return self.serialize_component

    def __repr__(self):
        return str(self.serialize)
