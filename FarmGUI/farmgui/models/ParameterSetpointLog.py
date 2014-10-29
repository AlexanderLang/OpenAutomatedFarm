"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import DateTime
from sqlalchemy.types import Float
from sqlalchemy import ForeignKey

from .meta import Base


class ParameterSetpointLog(Base):
    """
    classdocs
    """
    __tablename__ = 'ParameterSetpointLogs'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    parameter_id = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    setpoint = Column(Float, nullable=True)

    def __init__(self, parameter, time, setpoint):
        self.parameter = parameter
        self.time = time
        self.setpoint = setpoint
