"""
Created on Nov 17, 2013

@author: alex
"""

from farmgui.models import ParameterType
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.orm import relationship

from farmgui.models import Sensor
from farmgui.models import Display
from farmgui.models import ParameterLink
from farmgui.models import DeviceLink
from farmgui.models import Parameter
from farmgui.models import Device


class LogDiagram(Display):
    """
    classdocs
    """

    __tablename__ = 'LogDiagrams'

    _id = Column(SmallInteger,
                 ForeignKey('Displays._id'),
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    period = Column(Integer, nullable=False)
    parameter_links = relationship("ParameterLink",
                                   order_by="ParameterLink._id",
                                   backref='display',
                                   cascade='all, delete, delete-orphan')
    device_links = relationship('DeviceLink',
                                order_by='DeviceLink._id',
                                backref='display',
                                cascade='all, delete, delete-orphan')

    __mapper_args__ = {'polymorphic_identity': 'log_diagram'}

    def __init__(self, name, description, period):
        """
        Constructor
        :type sensor: Sensor
        :type parameter_type: ParameterType
        """
        Display.__init__(self, name, description)
        self.period = period

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        ret_dict = self.serialize_display
        ret_dict['period'] = self.period
        pls = []
        for pl in self.parameter_links:
            pls.append(pl.serialize)
        ret_dict['parameter_links'] = pls
        dls = []
        for dl in self.device_links:
            dls.append(dl.serialize)
        ret_dict['device_links'] = dls
        return ret_dict


def init_log_diagrams(db_session):
    # query parameters and devices
    T_i = db_session.query(Parameter).filter_by(name='Inside Air Temperature').one()
    T_o = db_session.query(Parameter).filter_by(name='Outside Air Temperature').one()
    M_f = db_session.query(Device).filter_by(name='Exhaust Fan').one()
    dia = LogDiagram('Air Temperature Diagram', 'measuring parameters and influencing devices', 7200)
    dia.parameter_links.append(ParameterLink(dia, T_i, 'value', '#aa0000'))
    dia.parameter_links.append(ParameterLink(dia, T_i, 'setpoint', '#ff0000'))
    dia.parameter_links.append(ParameterLink(dia, T_o, 'value', '#0000aa'))
    dia.device_links.append(DeviceLink(dia, M_f, 'value', '#00aa00'))
    db_session.add(dia)