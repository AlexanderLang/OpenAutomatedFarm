"""
Created on Oct 15, 2014

@author: alex
"""

from datetime import timedelta

from farmgui.regulators import Regulator
from farmgui.regulators import RegulatorProperty


class ProportionalPulse(Regulator):

    def __init__(self):
        Regulator.__init__(self, 'Delayed PI Regulator')
        self.inputs['value'] = RegulatorProperty(0, 'Value')
        self.inputs['setpoint'] = RegulatorProperty(0, 'Setpoint')
        self.inputs['activate'] = RegulatorProperty(0, 'Pulse activation signal')
        self.outputs['output'] = RegulatorProperty(0, 'Pulsed output signal')
        self.constants['t_off'] = RegulatorProperty(60, 'Output low period (seconds)')
        self.constants['P'] = RegulatorProperty(10, 'Proportional constant')
        self.last_change = None
        self.state = 'ready'

    def execute(self, inputs):
        if self.is_executable(inputs):
            t_on = timedelta(seconds=((inputs['setpoint'] - inputs['value']) * self.constants['P'].value))
            if self.state == 'ready':
                if inputs['activate'] == 1:
                    self.last_change = inputs['now']
                    self.state = 'on'
                    return {'output': 1}
                else:
                    return {'output': 0}
            elif self.state == 'on':
                diff = inputs['now'] - self.last_change
                if diff > t_on:
                    self.last_change = inputs['now']
                    self.state = 'off'
                    return {'output': 0}
                else:
                    return {'output': 1}
            else:
                diff = inputs['now'] - self.last_change
                if diff > timedelta(seconds=self.constants['t_off'].value):
                    self.state = 'ready'
                return {'output': 0}
        return {'output': None}
