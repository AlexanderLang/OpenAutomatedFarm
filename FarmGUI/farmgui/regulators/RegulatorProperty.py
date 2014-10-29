"""
Created on Oct 15, 2014

@author: alex
"""

class RegulatorProperty(object):

    _description = ''
    _value = 0.0
    _min = None
    _max = None

    def __init__(self, value, description, minimum=None, maximum=None):
        self._value = value
        self._description = description
        self._min = minimum
        self._max = maximum

    @property
    def description(self):
        return self._description

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if self._min is not None:
            if val < self._min:
                val = self._min
        if self._max is not None:
            if val > self._max:
                val = self._max
        self._value = val

