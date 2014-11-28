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


class DeviceSetpointLog(Base):
    """
    classdocs
    """
    __tablename__ = 'DeviceSetpointLogs'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    device_id = Column(SmallInteger, ForeignKey('Devices._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    setpoint = Column(Float, nullable=True)

    def __init__(self, device, time, setpoint):
        self.device = device
        self.time = time
        self.setpoint = setpoint

    @property
    def id(self):
        return self._id

    @staticmethod
    def log(db_session, device, time, setpoint):
        query = db_session.query(DeviceSetpointLog).filter_by(device_id=device.id)
        old_logs = query.order_by(DeviceSetpointLog.time.desc()).limit(2).all()
        insert_new_setpoint = False
        if len(old_logs) < 2:
            # there aren't enought logs jet for interpolation
            insert_new_setpoint = True
        else:
            # verify that last log values are numbers
            y1 = old_logs[1].setpoint
            y2 = old_logs[0].setpoint
            if y1 is None and y2 is None and setpoint is None:
                # still no value, update last log
                old_logs[0].time = time
                return
            elif y1 is not None and y2 is None:
                # (only)last value is None, add new entry (no matter if None or Number)
                insert_new_setpoint = True
            elif y1 is not None and y2 is not None and setpoint is None:
                # first None value, log it
                insert_new_setpoint = True
            else:
                # try to interpolate
                t1 = old_logs[1].time
                t2 = old_logs[0].time
                if y1 is None or y2 is None:
                    insert_new_setpoint = True
                else:
                    dt = (t2 - t1).total_seconds()
                    k_old = None
                    if dt != 0:
                        k_old = (y2 - y1) / dt
                    k_new = None
                    dt = (time - t2).total_seconds()
                    if dt != 0:
                        k_new = (setpoint - y2) / dt
                    if k_old is not None and k_new is not None:
                        if k_new != 0:
                            diff = abs((k_new - k_old) / k_new)
                            if diff < 0.02:
                                # new point is on straight line with old values, update last entry
                                old_logs[0].time = time
                                old_logs[0].setpoint = setpoint
                            else:
                                insert_new_setpoint = True
                        else:
                            if k_old == 0:
                                # value is constant, update last log entry
                                old_logs[0].time = time
                                old_logs[0].setpoint = setpoint
                            else:
                                # value started being constant, add new entry
                                insert_new_setpoint = True
                    else:
                        insert_new_setpoint = True
        if insert_new_setpoint:
            db_session.add(DeviceSetpointLog(device, time, setpoint))
