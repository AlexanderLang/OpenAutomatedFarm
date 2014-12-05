"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from farmgui.models import Base


class ComponentOutput(Base):
    """
    classdocs
    """
    __tablename__ = 'ComponentOutputs'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    component_id = Column(SmallInteger, ForeignKey('Components._id'))
    name = Column(Unicode(250), nullable=False)

    _value = None

    def __init__(self, component, name):
        self.component = component
        self.name = name

    def update_value(self, redis_conn, value, timeout):
        self._value = value
        redis_conn.setex(self.redis_key, self._value, timeout)

    @property
    def id(self):
        return self._id

    @property
    def redis_key(self):
        return 'co'+str(self._id)

    @property
    def value(self):
        return self._value

    @property
    def serialize(self):
        """Return data in serializeable format"""
        return {'id': self._id,
                'component_id': self.component_id,
                'name': self.name,
                'redis_key': self.redis_key}

    def __repr__(self):
        return str(self.serialize)
