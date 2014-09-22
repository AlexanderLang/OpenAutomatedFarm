"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base
from .meta import serialize
from .RegulatorConfig import RegulatorConfig


class Regulator(Base):
    """
    classdocs
    """

    __tablename__ = 'Regulators'

    _id = Column(SmallInteger,
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    component_id = Column(SmallInteger,
                          ForeignKey('FarmComponents._id'),
                          nullable=False)
    component = relationship('FarmComponent', back_populates='regulators')
    name = Column(Unicode(250),
                  nullable=False,
                  unique=False)
    regulator_type_id = Column(SmallInteger,
                               ForeignKey('RegulatorTypes._id'),
                               nullable=False)
    _regulator_type = relationship('RegulatorType')
    description = Column(Text,
                         nullable=True)
    input_parameter_id = Column(SmallInteger,
                       ForeignKey('Parameters._id'),
                       nullable=False)
    input_parameter = relationship("Parameter")
    output_device_id = Column(SmallInteger,
                       ForeignKey('Devices._id'),
                       nullable=False)
    output_device = relationship("Device")
    config = relationship('RegulatorConfig', backref='regulator', cascade="all, delete, delete-orphan")

    def __init__(self, component, name, regulator_type, input_parameter, output_device, description):
        """
        Constructor
        :type sensor: Sensor
        :type component: FarmComponent
        :type parameter_type: ParameterType
        """
        self.component = component
        self.component_id = component.id
        self.name = name
        self.regulator_type = regulator_type
        self.regulator_type_id = regulator_type.id
        self.input_parameter = input_parameter
        self.input_parameter_id = input_parameter.id
        self.output_device = output_device
        self.output_device_id = output_device.id
        self.description = description

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        return {
            '_id': self.id,
            'name': self.name,
            'description': self.description,
            'component': serialize(self.component),
            'regulator_type': serialize(self.regulator_type),
            'input_parameter': self.input_parameter.serialize,
            'output_device': self.output_device.serialize
        }

    @property
    def regulator_type(self):
        return self._regulator_type

    @regulator_type.setter
    def regulator_type(self, value):
        self._regulator_type = value
        if value.name == 'P':
            while len(self.config)>1:
                # delete unneeded config
                del self.config[-1]
            if len(self.config) == 0:
                new_conf = RegulatorConfig(self, 'K_p', '20', 'proportional gain')
                self.config.append(new_conf)
            else:
                self.config[0].name = 'K_p'
                self.config[0].value = 20
        elif value.name == 'PI':
            while len(self.config) > 2:
                # delete unneeded config
                del self.config[-1]
            if len(self.config) == 0:
                new_conf = RegulatorConfig(self, 'K_p', '20', 'proportional gain')
                self.config.append(new_conf)
            else:
                self.config[0].name = 'K_p'
                self.config[0].value = 20
            if len(self.config) < 2:
                new_conf = RegulatorConfig(self, 'K_i', '0.5', 'integral gain')
                self.config.append(new_conf)

    def calculate_output(self, setpoint, value, t_i):
        if self.regulator_type.name == 'P':
            output = (setpoint - value)*float(self.config[0].value)
        if self.regulator_type.name == 'PI':
            d = setpoint - value
            self.esum = self.esum + d
            if self.esum > 200:
                self.esum = 200
            elif self.esum < -200:
                self.esum = -200
            P = d * float(self.config[0].value)
            I = self.esum * t_i * float(self.config[1].value)
            output = P + I
        if output > 100:
            output = 100
        if output < 0:
            output = 0
        return output



def init_regulators(db_session):
    pass
