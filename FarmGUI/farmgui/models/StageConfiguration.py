"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Time
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base


class StageConfiguration(Base):
    """
    classdocs
    """
    __tablename__ = 'StageConfigurations'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    stageId = Column(BigInteger, ForeignKey('Stages._id'), nullable=False)
    parameterId = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
    parameter = relationship("Parameter")
    time = Column(Time, nullable=False)
    setpoint = Column(Float, nullable=False)
    upperLimit = Column(Float, nullable=False)
    lowerLimit = Column(Float, nullable=False)

    def __init__(self, stage, parameter, time, setpoint, upper_limit, lower_limit):
        """
        Constructor
        """
        self.stage = stage
        self.parameter = parameter
        self.parameterId = parameter.id
        self.time = time
        self.setpoint = setpoint
        self.upperLimit = upper_limit
        self.lowerLimit = lower_limit


def init_stage_configurations(db_session):
    pass

