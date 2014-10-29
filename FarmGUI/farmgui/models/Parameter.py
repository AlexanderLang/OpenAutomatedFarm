"""
Created on Nov 17, 2013

@author: alex
"""

from datetime import timedelta
from farmgui.models import ParameterType
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.orm import relationship
import logging

from farmgui.models import Component
from farmgui.models import ComponentOutput
from farmgui.models import serialize
from farmgui.models import ParameterValueLog
from farmgui.models import ParameterSetpointLog
from farmgui.models import SetpointInterpolation
from farmgui.models import CalendarEntry
from farmgui.models import Sensor


class Parameter(Component):
    """
    classdocs
    """

    __tablename__ = 'Parameters'

    _id = Column(SmallInteger,
                 ForeignKey('Components._id'),
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    parameter_type_id = Column(SmallInteger,
                               ForeignKey('ParameterTypes._id'),
                               nullable=False)
    parameter_type = relationship('ParameterType')
    sensor_id = Column(SmallInteger,
                       ForeignKey('Sensors._id'),
                       nullable=True)
    sensor = relationship("Sensor", lazy='joined')
    value_logs = relationship("ParameterValueLog",
                              order_by="ParameterValueLog.time",
                              cascade='all, delete, delete-orphan')
    setpoint_logs = relationship("ParameterSetpointLog",
                                 order_by="ParameterSetpointLog.time",
                                 cascade='all, delete, delete-orphan')
    calendar = relationship('CalendarEntry',
                            order_by='CalendarEntry.entry_number',
                            cascade='all, delete, delete-orphan')

    __mapper_args__ = {'polymorphic_identity': 'parameter'}

    current_calendar_entry = None

    def __init__(self, name, parameter_type, sensor, description):
        """
        Constructor
        :type sensor: Sensor
        :type parameter_type: ParameterType
        """
        Component.__init__(self, name, description)
        self.parameter_type = parameter_type
        self.sensor = sensor
        if sensor is not None:
            self._outputs['value'] = ComponentOutput(self, 'value')
            self._outputs['setpoint'] = ComponentOutput(self, 'setpoint')
        else:
            self._outputs['value'] = ComponentOutput(self, 'value')
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
        if self.current_calendar_entry is None:
            logging.warning(self.name + ': could not find calendar entry for ' + str(present))

    def get_setpoint(self, cultivation_start, time):
        if self.current_calendar_entry is None:
            self.configure_calendar(cultivation_start, time)
        elif self.current_calendar_entry.end_time < time:
            self.configure_calendar(cultivation_start, time)
        if self.current_calendar_entry is not None:
            return self.current_calendar_entry.get_value_at(time)
        return None

    def update_setpoint(self, cultivation_start, time, redis_conn):
        value = self.get_setpoint(cultivation_start, time)
        redis_conn.set(self._outputs['setpoint'].redis_key, value)


    def update_value(self, redis_conn):
        value = redis_conn.get(self.sensor.redis_key)
        redis_conn.set(self._outputs['value'].redis_key, value)

    def log_setpoint(self, time, redis_conn):
        value_str = redis_conn.get(self._outputs['setpoint'].redis_key)
        value = None
        remove_uneeded = True
        if value_str != b'None':
            value = float(value_str)
        try:
            old_1 = self.setpoint_logs[-2].setpoint
            old_2 = self.setpoint_logs[-1].setpoint
        except IndexError:
            old_1 = None
            old_2 = None
            remove_uneeded = False
        if old_2 == value and old_1 == value:
            # value is constant, remove last entry (if there are at least 2 entries)
            if remove_uneeded:
                self.setpoint_logs.remove(self.setpoint_logs[-1])
        else:
            print('o1='+str(old_1)+' o2='+str(old_2)+' sp='+str(value))
        # add new log entry
        new_log = ParameterSetpointLog(self, time, value)
        self.setpoint_logs.append(new_log)

    def log_value(self, time, redis_conn):
        value_str = redis_conn.get(self._outputs['value'].redis_key)
        value = None
        if value_str is not None:
            value = float(value_str)
        log_new = True
        try:
            old_1 = self.value_logs[-2].value
            old_2 = self.value_logs[-1].value
        except IndexError:
            old_1 = None
            old_2 = None
        if old_2 == value and old_1 == value:
            # value is constant, update time of last entry
            try:
                self.value_logs[-1].time = time
                log_new = False
            except IndexError:
                log_new = True
        if log_new:
            # value changed, add new log entry
            new_log = ParameterValueLog(self, time, value)
            self.value_logs.append(new_log)

    @property
    def id(self):
        return self._id

    @property
    def order(self):
        return -1

    @property
    def serialize(self):
        """Return data in serializeable format"""
        ret_dict = Component.serialize(self)
        ret_dict['parameter_type'] = serialize(self.parameter_type)
        ret_dict['sensor'] = self.sensor.serialize
        return ret_dict


def init_parameters(db_session):
    # query types
    temp_type = db_session.query(ParameterType).filter_by(name='Temperature').first()
    humidity_type = db_session.query(ParameterType).filter_by(name='Humidity').first()
    ph_type = db_session.query(ParameterType).filter_by(name='pH').first()
    ec_type = db_session.query(ParameterType).filter_by(name='Conductivity').first()
    vol_type = db_session.query(ParameterType).filter_by(name='Volume').first()
    # query interpolations
    temp_inter = db_session.query(SetpointInterpolation).filter_by(name='Temperature Interpolation (long day)').one()
    # query sensors
    temp1_sensor = db_session.query(Sensor).filter_by(name='T1').first()
    humi1_sensor = db_session.query(Sensor).filter_by(name='H1').first()
    temp2_sensor = db_session.query(Sensor).filter_by(name='T2').first()
    humi2_sensor = db_session.query(Sensor).filter_by(name='H2').first()
    temp3_sensor = db_session.query(Sensor).filter_by(name='T3').first()
    # create Parameter
    new_param = Parameter('Inside Air Temperature', temp_type, temp1_sensor, '')
    # set calendar
    new_param.calendar.append(CalendarEntry(new_param, 1, temp_inter))
    new_param.calendar.append(CalendarEntry(new_param, 2, temp_inter))
    new_param.calendar.append(CalendarEntry(new_param, 3, temp_inter))
    new_param.calendar.append(CalendarEntry(new_param, 4, temp_inter))
    db_session.add(new_param)
    new_param = Parameter('Inside Air Humidity', humidity_type, humi1_sensor, '')
    db_session.add(new_param)
    new_param = Parameter('Outside Air Temperature', temp_type, temp2_sensor, '')
    db_session.add(new_param)
    new_param = Parameter('Outside Air Humidity', humidity_type, humi2_sensor, '')
    db_session.add(new_param)
    new_param = Parameter('Nutrient Tank Water Temperature', temp_type, temp3_sensor, '')
    db_session.add(new_param)
    new_param = Parameter('Nutrient Tank Water pH', ph_type, temp1_sensor, '')
    db_session.add(new_param)
    new_param = Parameter('Nutrient Tank Water EC', ec_type, temp1_sensor, '')
    db_session.add(new_param)
    new_param = Parameter('Nutrient Tank Water Content', vol_type, temp1_sensor, '')
    db_session.add(new_param)
