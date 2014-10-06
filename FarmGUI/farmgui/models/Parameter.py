"""
Created on Nov 17, 2013

@author: alex
"""

from datetime import timedelta
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base
from .meta import serialize
from .ParameterLog import ParameterLog


class Parameter(Base):
    """
    classdocs
    """

    __tablename__ = 'Parameters'

    _id = Column(SmallInteger,
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    component_id = Column(SmallInteger,
                          ForeignKey('FarmComponents._id'),
                          nullable=False)
    component = relationship('FarmComponent', back_populates='parameters')
    name = Column(Unicode(250),
                  nullable=False,
                  unique=False)
    parameter_type_id = Column(SmallInteger,
                               ForeignKey('ParameterTypes._id'),
                               nullable=False)
    parameter_type = relationship('ParameterType')
    description = Column(Text,
                         nullable=True)
    sensor_id = Column(SmallInteger,
                       ForeignKey('Sensors._id'),
                       nullable=True)
    sensor = relationship("Sensor")
    logs = relationship("ParameterLog",
                        order_by="ParameterLog.time",
                        cascade='all, delete, delete-orphan')
    calendar = relationship('CalendarEntry',
                            order_by='CalendarEntry.entry_number',
                            cascade='all, delete, delete-orphan')

    def __init__(self, component, name, parameter_type, sensor, description):
        """
        Constructor
        :type sensor: Sensor
        :type component: FarmComponent
        :type parameter_type: ParameterType
        """
        self.component = component
        self.component_id = component.id
        self.name = name
        self.parameter_type = parameter_type
        self.parameter_type_id = parameter_type.id
        self.sensor = sensor
        if sensor is not None:
            self.sensor_id = sensor.id
        self.description = description
        self.current_calendar_entry = None

    def configure_calendar(self, cultivation_start, present):
        start_time = cultivation_start
        for entry in self.calendar:
            end_time = start_time + timedelta(seconds=entry.interpolation.end_time)
            if end_time > present:
                # found current calendar entry
                entry.end_time = end_time
                self.current_calendar_entry = entry
            else:
                start_time = end_time
        self.current_calendar_entry = None

    def get_setpoint(self, time):
        if self.current_calendar_entry is None:
            return None
        if self.current_calendar_entry.end_time < time:
            return None
        entry = self.current_calendar_entry
        start_time = entry.end_time + timedelta(seconds=entry.interpolation.end_time)
        setpoint_time = time - start_time
        return entry.get_value_at(setpoint_time)

    def log_measurement(self, time, value):
        try:
            old_1 = self.logs[-2].value
            old_2 = self.logs[-1].value
            if old_2 == value and old_1 == value:
                # value is constant, update time on last entry
                self.logs[-1].time = time
            else:
                # add a new log entry
                new_log = ParameterLog(self, time, value)
                self.logs.append(new_log)
        except IndexError:
            new_log = ParameterLog(self, time, value)
            self.logs.append(new_log)

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
            'parameter_type': serialize(self.parameter_type),
            'sensor': self.sensor.serialize
        }


def init_parameters(db_session):
    pass
