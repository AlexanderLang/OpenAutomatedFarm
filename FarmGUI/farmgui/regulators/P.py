"""
Created on Oct 15, 2014

@author: alex
"""

from farmgui.regulators import Regulator
from farmgui.regulators import RegulatorProperty

class P(Regulator):

    def __init__(self):
        Regulator.__init__(self, 'P Regulator')
        self.inputs['diff'] = RegulatorProperty(0, 'difference between output and setpoint')
        self.constants['K_p'] = RegulatorProperty(1, 'Proportional constant')
        self.outputs['result'] = RegulatorProperty(0, 'Regulator output')

    def execute(self):
        if self.is_executable():
            self.outputs['result'].value = round(self.inputs['diff'].value * self.constants['K_p'].value, 2)