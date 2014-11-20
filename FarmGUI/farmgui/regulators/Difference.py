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

    def execute(self, inputs):
        ret_dict = {}
        if self.is_executable(inputs):
            ret_dict['result'] = round(inputs['a'] - inputs['b'], 2)
        else:
            ret_dict['result'] = None
        return ret_dict