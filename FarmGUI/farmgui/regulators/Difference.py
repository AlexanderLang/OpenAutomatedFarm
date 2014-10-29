"""
Created on Oct 15, 2014

@author: alex
"""

from farmgui.regulators import Regulator
from farmgui.regulators import RegulatorProperty

class Difference(Regulator):

    def __init__(self):
        Regulator.__init__(self, 'Difference')
        self.inputs['a'] = RegulatorProperty(0, 'input 1')
        self.inputs['b'] = RegulatorProperty(0, 'input 2')
        self.outputs['result'] = RegulatorProperty(0, 'Result (a-b)')

    def execute(self):
        if self.is_executable():
            self.outputs['result'].value = round(self.inputs['a'].value - self.inputs['b'].value, 2)