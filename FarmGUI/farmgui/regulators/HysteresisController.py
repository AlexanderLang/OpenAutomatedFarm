"""
Created on Oct 15, 2014

@author: alex
"""

from farmgui.regulators import Regulator
from farmgui.regulators import RegulatorProperty


class HysteresisController(Regulator):

    def __init__(self):
        Regulator.__init__(self, 'Two Level Regulator')
        self.inputs['value'] = RegulatorProperty(0, '')
        self.inputs['setpoint'] = RegulatorProperty(0, '')
        self.constants['uh'] = RegulatorProperty(1, 'Upper Hysteresis')
        self.constants['lh'] = RegulatorProperty(1, 'Lower Hysteresis')
        self.outputs['inc'] = RegulatorProperty(0, 'Increment output')
        self.outputs['dec'] = RegulatorProperty(0, 'Decrement output')
        self.state = 'OK'

    def execute(self, inputs):
        ret_dict = {}
        if self.is_executable(inputs):
            diff = inputs['setpoint'] - inputs['value']
            uh = self.constants['uh'].value
            lh = self.constants['lh'].value
            if self.state == 'OK':
                if diff > -uh:
                    ret_dict['inc'] = 0
                    ret_dict['dec'] = 1
                    self.state = 'dec'
                elif diff > lh:
                    ret_dict['inc'] = 1
                    ret_dict['dec'] = 0
                    self.state = 'inc'
                else:
                    ret_dict['inc'] = 0
                    ret_dict['dec'] = 0
                    self.state = 'OK'
            elif self.state == 'dec':
                if diff < 0:
                    ret_dict['inc'] = 0
                    ret_dict['dec'] = 1
                else:
                    ret_dict['inc'] = 0
                    ret_dict['dec'] = 0
                    self.state = 'OK'
            else:
                if diff > 0:
                    ret_dict['inc'] = 1
                    ret_dict['dec'] = 0
                else:
                    ret_dict['inc'] = 0
                    ret_dict['dec'] = 0
                    self.state = 'OK'
        else:
            ret_dict['inc'] = None
            ret_dict['dec'] = None
        return ret_dict