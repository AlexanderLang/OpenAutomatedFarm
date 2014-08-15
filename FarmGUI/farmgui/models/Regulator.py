"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Float
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base


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
    regulator_type = relationship('RegulatorType')
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


def init_regulators(db_session):
    pass
