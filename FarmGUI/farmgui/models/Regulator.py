"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode

from farmgui.models import Component
from farmgui.models import ComponentInput
from farmgui.models import ComponentOutput
from farmgui.models import ComponentProperty
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

    real_regulator = None

    def __init__(self, name, algorithm_name, description):
        """
        Constructor
        """
        Component.__init__(self, name, description)
        self._algorithm_name = algorithm_name
        self.real_regulator = regulator_factory(self._algorithm_name)
        self.initialize_regulator_db()


    @property
    def id(self):
        return self._id

    @property
    def serialize(self):
        """Return data in serializeable format"""
        ret_dict = Component.serialize(self)
        ret_dict['algorithm_name'] = self._algorithm_name
        return ret_dict

    @property
    def algorithm_name(self):
        return self._algorithm_name

    def execute(self, redis_con):
        if self.real_regulator is None:
            self.real_regulator = regulator_factory(self._algorithm_name)
            # get constants
            for const_key in self._properties:
                self.real_regulator.constants[const_key].value = float(self._properties[const_key].value)
        # get inputs
        execute = True
        for in_key in self._inputs:
            conn_out = self._inputs[in_key].connected_output
            if conn_out is not None:
                value_str = redis_con.get(conn_out.redis_key)
                value = None
                if value_str is not None:
                    value = float(value_str)
                self.real_regulator.inputs[in_key].value = value
            else:
                execute = False
        # execute
        if execute:
            self.real_regulator.execute()
            # set outputs
            for out_key in self._outputs:
                value = self.real_regulator.outputs[out_key].value
                redis_con.set(self._outputs[out_key].redis_key, str(value))


    def initialize_regulator_db(self):
        """

        :param db_regulator:
        """
        for in_key in self.real_regulator.inputs:
            self._inputs[in_key] = ComponentInput(self, in_key, None)
        for out_key in self.real_regulator.outputs:
            self._outputs[out_key] = ComponentOutput(self, out_key)
        for const_key in self.real_regulator.constants:
            self._properties[const_key] = ComponentProperty(self, const_key, str(self.real_regulator.constants[const_key].value))


def init_regulators(db_session):
    air_temp_diff = Regulator('Air Temperature Difference', 'Difference', '')
    air_temp_reg = Regulator('Air Temperature Regulator', 'PI', '')
    test_reg = Regulator('Test Regulator', 'P', '')
    # make connections
    inside_temp = db_session.query(Parameter).filter_by(name='Inside Air Temperature').one()
    exhaust_fan = db_session.query(Device).filter_by(name='Exhaust Fan').one()
    air_temp_diff.connect_input('a', inside_temp.outputs['value'])
    air_temp_diff.connect_input('b', inside_temp.outputs['setpoint'])
    air_temp_reg.connect_input('diff', air_temp_diff.outputs['result'])
    exhaust_fan.connect_input('value', air_temp_reg.outputs['result'])
    db_session.add(air_temp_diff)
    db_session.add(air_temp_reg)
    db_session.add(test_reg)

