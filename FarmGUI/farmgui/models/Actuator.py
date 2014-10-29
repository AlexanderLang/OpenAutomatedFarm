"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import Float
from sqlalchemy.types import SmallInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from farmgui.models import serialize
from farmgui.models import Hardware
from farmgui.models import DeviceType


class Actuator(Hardware):
    """
    classdocs
    """
    __tablename__ = 'Actuators'

    _id = Column(SmallInteger, ForeignKey('Hardware._id'), primary_key=True, autoincrement=True, nullable=False, unique=True)
    device_type_id = Column(SmallInteger,
                               ForeignKey('DeviceTypes._id'),
                               nullable=False)
    device_type = relationship('DeviceType')
    default_value = Column(Float, nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'actuator'}

    def __init__(self, periphery_controller, index, name, device_type, default_value):
        Hardware.__init__(self, periphery_controller, index, name, '')
        self.device_type = device_type
        self.default_value = default_value

    @property
    def redis_key(self):
        return 'p'+str(self.periphery_controller_id)+'.a'+str(self.index)+'.value'

    @property
    def serialize(self):
        """Return data in serializeable format"""
        return {
            '_id': self.id,
            'periphery_controller': serialize(self.periphery_controller),
            'name': self.name,
            'device_type': serialize(self.device_type)
        }


def init_actuators(db_session, pc):
    lin_type = db_session.query(DeviceType).filter_by(name='Linear').one()
    on_off_type = db_session.query(DeviceType).filter_by(name='ON/OFF').one()
    pc.actuators.append(Actuator(pc, 0, 'L1', lin_type, 0))
    pc.actuators.append(Actuator(pc, 1, 'B1', on_off_type, 0))