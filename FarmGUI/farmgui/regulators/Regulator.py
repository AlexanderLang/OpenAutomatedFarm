"""
Created on Oct 15, 2014

@author: alex
"""


class Regulator(object):

    def __init__(self, description):
        self.description = description
        self.constants = dict()
        self.inputs = dict()
        self.outputs = dict()

    def execute(self):
        pass

    def is_executable(self):
        for in_key in self.inputs:
            if self.inputs[in_key].value is None:
                return False
        return True