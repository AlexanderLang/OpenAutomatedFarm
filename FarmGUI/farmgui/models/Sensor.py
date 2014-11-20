"""
Created on Feb 15, 2014

@author: alex
"""
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship

from farmgui.models import serialize
from farmgui.models import Hardware
from farmgui.models import ParameterType


class Sensor(Hardware):
    """
    classdocs
    """
    __tablename__ = 'Sensors'

    _id = Column(SmallInteger, ForeignKey('Hardware._id'), primary_key=True, autoincrement=True, nullable=False, unique=True)
    parameter_type_id = Column(SmallInteger, ForeignKey('ParameterTypes._id'), nullable=False)
    parameter_type = relationship('ParameterType')
    precision = Column(Float(), nullable=False)
    minimum = Column(Float(), nullable=False)
    maximum = Column(Float(), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'sensor'}

    def __init__(self, periphery_controller, index, name, parameter_type, precision, minimum, maximum):
        Hardware.__init__(self, periphery_controller, index, name, '')
        self.parameter_type = parameter_type
        self.precision = precision
        self.minimum = minimum
        self.maximum = maximum
        self.last_measured = datetime.now()

    @property
    def redis_key(self):
        return 'p'+str(self.periphery_controller_id)+'.s'+str(self.index)+'.value'

    @property
    def serialize(self):
        """Return data in serializeable format"""
        return {
            '_id': self.id,
            'periphery_controller': serialize(self.periphery_controller),
            'name': self.name,
            'parameter_type': serialize(self.parameter_type),
            'precision': self.precision,
            'minimum': self.minimum,
            'maximum': self.maximum
        }


def init_sensors(db_session, pc):
    temp_type = db_session.query(ParameterType).filter_by(name='Temperature').one()
    humi_type = db_session.query(ParameterType).filter_by(name='Humidity').one()
    pc.sensors.append(Sensor(pc, 0, 'T1', temp_type, 0.2, 0, 100))
    pc.sensors.append(Sensor(pc, 1, 'T2', temp_type, 0.2, 10, 40))
    pc.sensors.append(Sensor(pc, 2, 'T3', temp_type, 0.2, 10, 45))
    pc.sensors.append(Sensor(pc, 3, 'H1', humi_type, 2, 20, 95))
    pc.sensors.append(Sensor(pc, 4, 'H2', humi_type, 2, 20, 95))
    pc.sensors.append(Sensor(pc, 5, 'H3', humi_type, 2, 20, 95))
