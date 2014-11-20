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
        self.outputs['result'] = RegulatorProperty(0, 'Regulator output')
        self.esum = 0

    def execute(self, inputs):
        ret_dict = {}
        if self.is_executable(inputs):
            p = inputs['diff'] * self.constants['K_p'].value
            self.esum += inputs['diff']
            i = self.constants['K_i'].value * self.constants['T_i'].value * self.esum
            ret_dict['result'] = round(p + i, 2)
        return ret_dict