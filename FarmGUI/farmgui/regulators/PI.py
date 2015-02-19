"""
Created on Oct 15, 2014

@author: alex
"""

from farmgui.regulators import Regulator
from farmgui.regulators import RegulatorProperty


class PI(Regulator):

    def __init__(self):
        Regulator.__init__(self, 'PI Regulator')
        self.inputs['diff'] = RegulatorProperty(0, 'difference between output and setpoint')
        self.constants['K_p'] = RegulatorProperty(1, 'Proportional constant')
        self.constants['K_i'] = RegulatorProperty(0.1, 'Integral constant')
        self.constants['T_i'] = RegulatorProperty(1, 'Sampling time interval')
        self.constants['min'] = RegulatorProperty(0, 'Minimum Output value')
        self.constants['max'] = RegulatorProperty(0, 'Maximum Output value')
        self.outputs['result'] = RegulatorProperty(0, 'Regulator output')
        self.esum = 0

    def execute(self, inputs):
        ret_dict = {}
        if self.is_executable(inputs):
            p = inputs['diff'] * self.constants['K_p'].value
            self.esum += inputs['diff']
            self.limit_esum()
            i = self.constants['K_i'].value * self.constants['T_i'].value * self.esum
            ret_dict['result'] = round(p + i, 2)
            if ret_dict['result'] > self.constants['max']:
                ret_dict['result'] = self.constants['max']
            elif ret_dict['result'] < self.constants['min']:
                ret_dict['result'] = self.constants['min']
        else:
            ret_dict['result'] = None
        return ret_dict

    def limit_esum(self):
        max_esum = 200
        if self.esum > max_esum:
            self.esum = max_esum
        elif self.esum < -max_esum:
            self.esum = -max_esum