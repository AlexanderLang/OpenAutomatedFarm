"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from farmgui.models import Component
from farmgui.models import Parameter
from farmgui.models import Device

from farmgui.regulators import regulator_factory


class Regulator(Component):
    """
    classdocs
    """

    __tablename__ = 'Regulators'

    _id = Column(SmallInteger,
                 ForeignKey('Components._id'),
                 primary_key=True,
                 autoincrement=True,
                 nullable=False,
                 unique=True)
    _algorithm_name = Column(Unicode(100),
                             nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'regulator'}

    def __init__(self, name, algorithm_name, description):
        """
        Constructor
        """
        Component.__init__(self, name, description)
        self.algorithm_name = algorithm_name

    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        ret_dict = self.serialize_component
        ret_dict['algorithm_name'] = self._algorithm_name
        return ret_dict

    @property
    def algorithm_name(self):
        return self._algorithm_name

    @algorithm_name.setter
    def algorithm_name(self, value):
        self._algorithm_name = value


def init_regulators(db_session):
    # query components needed for initialisation
    inside_temp = db_session.query(Parameter).filter_by(name='Inside Air Temperature').one()
    inside_humi = db_session.query(Parameter).filter_by(name='Inside Air Humidity').one()
    exhaust_fan = db_session.query(Device).filter_by(name='Exhaust Fan').one()
    root_mist_pump = db_session.query(Device).filter_by(name='Rootchamber Mist pump').one()

    # create regulators
    air_temp_diff = Regulator('Air Temperature Difference', 'Difference', '')
    real_reg = regulator_factory(air_temp_diff.algorithm_name)
    real_reg.initialize_db(air_temp_diff)
    air_temp_diff.inputs['a'].connected_output = inside_temp.outputs['value']
    air_temp_diff.inputs['b'].connected_output = inside_temp.outputs['setpoint']
    db_session.add(air_temp_diff)

    air_temp_reg = Regulator('Air Temperature Regulator', 'PI', '')
    real_reg = regulator_factory(air_temp_reg.algorithm_name)
    real_reg.initialize_db(air_temp_reg)
    air_temp_reg.inputs['diff'].connected_output = air_temp_diff.outputs['result']
    db_session.add(air_temp_reg)

    root_humidifier = Regulator('Root Humidifier', 'RootHumidifier', '')
    real_reg = regulator_factory(root_humidifier.algorithm_name)
    real_reg.initialize_db(root_humidifier)
    root_humidifier.inputs['T_i'].connected_output = inside_temp.outputs['value']
    root_humidifier.inputs['H_i'].connected_output = inside_humi.outputs['value']
    root_humidifier.inputs['T_i_sp'].connected_output = inside_temp.outputs['setpoint']
    root_humidifier.inputs['H_i_sp'].connected_output = inside_humi.outputs['setpoint']
    db_session.add(root_humidifier)

    # connect output device
    exhaust_fan.inputs['value'].connected_output = air_temp_reg.outputs['result']
    root_mist_pump.inputs['value'].connected_output = root_humidifier.outputs['pump']
