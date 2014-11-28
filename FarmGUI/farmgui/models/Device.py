"""
Created on Nov 17, 2013

@author: alex
"""

import logging
from datetime import timedelta
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

from farmgui.models import Component
from farmgui.models import ComponentInput
from farmgui.models import ComponentOutput
from farmgui.models import DeviceType
from farmgui.models import DeviceValueLog
from farmgui.models import DeviceSetpointLog
from farmgui.models import Actuator
from farmgui.models import SetpointInterpolation
from farmgui.models import DeviceCalendarEntry

from farmgui.communication import get_redis_number


class Device(Component):
    """
    classdocs
    """

    __tablename__ = 'Devices'

    _id = Column(SmallInteger,
                 ForeignKey('Components._id'),
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    device_type_id = Column(SmallInteger,
                               ForeignKey('DeviceTypes._id'),
                               nullable=False)
    device_type = relationship('DeviceType')
    actuator_id = Column(SmallInteger,
                         ForeignKey('Actuators._id'),
                         nullable=True)
    actuator = relationship("Actuator", lazy='joined', backref=backref("device", uselist=False))
    value_logs = relationship("DeviceValueLog",
                              order_by="DeviceValueLog.time",
                              backref='device',
                              cascade='all, delete, delete-orphan')
    setpoint_logs = relationship("DeviceSetpointLog",
                                 order_by="DeviceSetpointLog.time",
                                 backref='device',
                                 cascade='all, delete, delete-orphan')
    calendar = relationship('DeviceCalendarEntry',
                            order_by='DeviceCalendarEntry.entry_number',
                            cascade='all, delete, delete-orphan')
    current_calendar_entry = None
    old_value = None
    old_setpoint = None

    __mapper_args__ = {'polymorphic_identity': 'device'}

    def __init__(self, name, device_type, actuator, description):
        """
        Constructor
        """
        Component.__init__(self, name, description)
        self.device_type = device_type
        self.actuator = actuator
        if actuator is not None:
            self._inputs['value'] = ComponentInput(self, 'value', None)
            self._outputs['setpoint'] = ComponentOutput(self, 'setpoint')
        else:
            self._inputs['value'] = ComponentInput(self, 'value', None)
            self._outputs['setpoint'] = ComponentOutput(self, 'setpoint')

    def configure_calendar(self, cultivation_start, present):
        start_time = cultivation_start
        self.current_calendar_entry = None
        for entry in self.calendar:
            end_time = start_time + timedelta(seconds=entry.interpolation.end_time)
            if end_time > present:
                # found current calendar entry
                entry.end_time = end_time
                self.current_calendar_entry = entry
            else:
                start_time = end_time
        #if self.current_calendar_entry is None:
        #    logging.warning(self.name + ': could not find calendar entry for ' + str(present))

    def get_setpoint(self, cultivation_start, time):
        if self.current_calendar_entry is None:
            self.configure_calendar(cultivation_start, time)
        elif self.current_calendar_entry.end_time < time:
            self.configure_calendar(cultivation_start, time)
        if self.current_calendar_entry is not None:
            return self.current_calendar_entry.get_value_at(time)
        return None

    def update_setpoint(self, db_session, cultivation_start, time, redis_conn, timeout):
        value = self.get_setpoint(cultivation_start, time)
        self._outputs['setpoint'].update_value(redis_conn, value, timeout)
        DeviceSetpointLog.log(db_session, self, time, value)

    def update_value(self, db_session, redis_conn, now, timeout):
        if self.actuator is not None:
            value = get_redis_number(redis_conn, self._inputs['value'].redis_key)
            DeviceValueLog.log(db_session, self, now, value)
            self.old_value = value
            redis_conn.setex(self.actuator.redis_key, value, timeout)

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        ret_dict = self.serialize_component
        ret_dict['device_type'] = self.device_type.serialize
        if self.actuator is not None:
            ret_dict['actuator'] = self.actuator.serialize
        else:
            ret_dict['actuator'] = None
        return ret_dict


def init_devices(db_session):
    # query types
    lin_type = db_session.query(DeviceType).filter_by(name='Linear').one()
    bool_type = db_session.query(DeviceType).filter_by(name='On/OFF').one()
    # query actuators
    lin_act = db_session.query(Actuator).filter_by(name='L1').first()
    on_off_act = db_session.query(Actuator).filter_by(name='B1').first()
    # query interpolations
    test_inter = db_session.query(SetpointInterpolation).filter_by(name='Test Interpolation').one()
    red_inter = db_session.query(SetpointInterpolation).filter_by(name='Red Light Interpolation (long day)').one()
    # ceating devices
    new_dev = Device('Exhaust Fan', lin_type, lin_act, '')
    db_session.add(new_dev)
    new_dev = Device('Inside Air Circulation Fan', lin_type, None, '')
    new_dev.calendar.append(DeviceCalendarEntry(new_dev, 1, test_inter))
    new_dev.calendar.append(DeviceCalendarEntry(new_dev, 2, test_inter))
    db_session.add(new_dev)
    new_dev = Device('Rootchamber  Mist Circulation', lin_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Rootchamber Mist pump', bool_type, on_off_act, '')
    db_session.add(new_dev)
    new_dev = Device('Inside Red Illumination', lin_type, None, '')
    new_dev.calendar.append(DeviceCalendarEntry(new_dev, 1, red_inter))
    new_dev.calendar.append(DeviceCalendarEntry(new_dev, 2, red_inter))
    new_dev.calendar.append(DeviceCalendarEntry(new_dev, 3, red_inter))
    new_dev.calendar.append(DeviceCalendarEntry(new_dev, 4, red_inter))
    db_session.add(new_dev)
    new_dev = Device('Inside Blue Illumination', lin_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Inside White Illumination', lin_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Nutrient Tank Fresh-water pump', bool_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Nutrient Tank Waste-water pump', bool_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Nutrient Tank Acid pump', bool_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Nutrient Tank Fertilizer pump', bool_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('Nutrient Tank Supplement pump', bool_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('LED cooling pump', bool_type, None, '')
    db_session.add(new_dev)
    new_dev = Device('LED cooling fan', lin_type, None, '')
    db_session.add(new_dev)

