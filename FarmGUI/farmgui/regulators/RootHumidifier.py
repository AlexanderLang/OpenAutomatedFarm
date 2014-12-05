"""
Created on Oct 15, 2014

@author: alex
"""

from datetime import timedelta

from farmgui.regulators import Regulator
from farmgui.regulators import RegulatorProperty


class RootHumidifier(Regulator):

    def __init__(self):
        Regulator.__init__(self, 'Root Humidifier')
        self.inputs['T_i'] = RegulatorProperty(0, 'Inside Air Temperature')
        self.inputs['T_i_sp'] = RegulatorProperty(0, 'Inside Air Temperature Setpoint')
        self.inputs['H_i'] = RegulatorProperty(0, 'Inside Air Humidity')
        self.inputs['H_i_sp'] = RegulatorProperty(0, 'Inside Air Humidity Setpoint')
        self.outputs['pump'] = RegulatorProperty(0, 'Fog Pump')
        self.outputs['t_off'] = RegulatorProperty(0, 'Calculated Off Time')
        self.constants['t_on'] = RegulatorProperty(30, 'Pump on time')
        self.constants['t_off_min'] = RegulatorProperty(60, 'Pump min off time')
        self.constants['t_off_max'] = RegulatorProperty(180, 'Pump max off time')
        self.last_change = None
        self.pump_value = 0

    def execute(self, inputs):
        ret_dict = {}
        t_on = timedelta(seconds=self.constants['t_on'].value)
        if self.last_change is None:
            self.last_change = inputs['now']
        if self.is_executable(inputs):
            dT = inputs['T_i_sp'] - inputs['T_i']
            dH = inputs['H_i_sp'] - inputs['H_i']
            dt = self.constants['t_off_max'].value - self.constants['t_off_min'].value
            if dT < 0 <= dH:
                # too hot and too dry
                self.outputs['t_off'].value = self.constants['t_off_min'].value
            elif dT < 0 and dH < 0:
                # too hot and too wet
                self.outputs['t_off'].value = self.constants['t_off_min'].value + dt * 0.33
            elif dT >= 0 and dH >= 0:
                # too cold and too dry
                self.outputs['t_off'].value = self.constants['t_off_min'].value + dt * 0.66
            elif dT >= 0 > dH:
                # too cold and too wet
                self.outputs['t_off'].value = self.constants['t_off_max'].value

            t = inputs['now'] - self.last_change
            t_off = timedelta(seconds=self.outputs['t_off'].value)
            if self.pump_value == 0:
                # pump is off, turn on after t_off has passed
                if t >= t_off:
                    # time to turn on
                    self.pump_value = 1
                    self.last_change = inputs['now']
                else:
                    # still waiting
                    self.pump_value = 0
            else:
                # pump is on, turn off after t_on has passed
                if t >= t_on:
                    # time to turn off
                    self.pump_value = 0
                    self.last_change = inputs['now']
                else:
                    # still waiting
                    self.pump_value = 1

            ret_dict['t_off'] = self.outputs['t_off'].value
            ret_dict['pump'] = self.pump_value
        else:
            ret_dict['t_off'] = None
            ret_dict['pump'] = None
        return ret_dict