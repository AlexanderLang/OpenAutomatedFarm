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

from farmgui.models import Base


class ParameterValueLog(Base):
    """
    classdocs
    """
    __tablename__ = 'ParameterValueLogs'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    parameter_id = Column(SmallInteger, ForeignKey('Parameters._id'), nullable=False)
    time = Column(DateTime, nullable=False)
    value = Column(Float, nullable=True)

    def __init__(self, parameter, time, value):
        self.parameter = parameter
        self.time = time
        self.value = value

    @staticmethod
    def log(db_session, parameter, time, value, old_logs):
        if old_logs is None:
            query = db_session.query(ParameterValueLog).filter_by(parameter_id=parameter.id)
            old_logs = query.order_by(ParameterValueLog.time.desc()).limit(2).all()
        insert_new_value = False
        if len(old_logs) < 2:
            # there aren't enought logs jet for interpolation
            insert_new_value = True
        else:
            # verify that last log values are numbers
            y1 = old_logs[1].value
            y2 = old_logs[0].value
            if y1 is None and y2 is None and value is None:
                # still no value, update last log
                old_logs[0].time = time
                return old_logs
            elif y1 is not None and y2 is None:
                # (only)last value is None, add new entry (no matter if None or Number)
                insert_new_value = True
            elif y1 is not None and y2 is not None and value is None:
                # first None value, log it
                insert_new_value = True
            else:
                # try to interpolate
                t1 = old_logs[1].time
                t2 = old_logs[0].time
                if y1 is None or y2 is None:
                    insert_new_value = True
                else:
                    dt = (t2 - t1).total_seconds()
                    k_old = None
                    if dt != 0:
                        k_old = (y2 - y1) / dt
                    k_new = None
                    dt = (time - t2).total_seconds()
                    if dt != 0:
                        k_new = (value - y2) / dt
                    if k_old is not None and k_new is not None:
                        if k_new != 0:
                            diff = abs((k_new - k_old) / k_new)
                            if diff < 0.02:
                                # new point is on straight line with old values, update last entry
                                old_logs[0].time = time
                                old_logs[0].value = value
                            else:
                                insert_new_value = True
                        else:
                            if k_old == 0:
                                # value is constant, update last log entry
                                old_logs[0].time = time
                                old_logs[0].value = value
                            else:
                                # value started being constant, add new entry
                                insert_new_value = True
                    else:
                        insert_new_value = True
        if insert_new_value:
            new_log = ParameterValueLog(parameter, time, value)
            db_session.add(new_log)
            old_logs[:0] = [new_log]
            old_logs.pop()
        return old_logs

