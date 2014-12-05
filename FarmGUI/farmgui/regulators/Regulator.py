"""
Created on Oct 15, 2014

@author: alex
"""

from farmgui.models import ComponentInput
from farmgui.models import ComponentOutput
from farmgui.models import ComponentProperty


class Regulator(object):

    def __init__(self, description):
        self.description = description
        self.constants = dict()
        self.inputs = dict()
        self.outputs = dict()

    def execute(self, inputs):
        return {}

    def is_executable(self, inputs):
        for in_key in self.inputs:
            #print('  '+in_key+' = '+str(inputs[in_key]))
            if inputs[in_key] is None:
                return False
        return True

    def initialize(self, reg_model):
        for in_key in self.inputs:
            con_out = reg_model.inputs[in_key].connected_output
            if con_out is not None:
                self.inputs[in_key].value = con_out.redis_key
        for out_key in self.outputs:
            self.outputs[out_key].value = reg_model.outputs[out_key].redis_key
        for const_key in self.constants:
            self.constants[const_key].value = float(reg_model.properties[const_key].value)

    def initialize_db(self, reg_model):
        """

        """
        # add needed inputs
        inputs = {}
        for in_key in self.inputs:
            if in_key not in reg_model.inputs:
                inputs[in_key] = ComponentInput(reg_model, in_key, None)
            else:
                inputs[in_key] = reg_model.inputs[in_key]
        reg_model._inputs = inputs
        # remove unneeded inputs
        del_keys = []
        for in_key in reg_model._inputs:
            if in_key not in self.inputs:
                del_keys.append(in_key)
        for del_key in del_keys:
            reg_model._inputs.pop(del_key, None)
        # add needed outputs
        outputs = {}
        for out_key in self.outputs:
            if out_key not in reg_model.outputs:
                outputs[out_key] = ComponentOutput(reg_model, out_key)
            else:
                outputs[out_key] = reg_model.outputs[out_key]
        reg_model._outputs = outputs
        # remove unneeded outputs
        del_keys = []
        for out_key in reg_model._outputs:
            if out_key not in self.outputs:
                del_keys.append(out_key)
        for del_key in del_keys:
            reg_model._outputs.pop(del_key, None)
        # add needed constants
        constants = {}
        for const_key in self.constants:
            if const_key not in reg_model.properties:
                constants[const_key] = ComponentProperty(reg_model, const_key, str(self.constants[const_key].value))
            else:
                constants[const_key] = reg_model._properties[const_key]
        reg_model._properties = constants
        # remove unneeded constants
        del_keys = []
        for const_key in reg_model.properties:
            if const_key not in self.constants:
                del_keys.append(const_key)
        for del_key in del_keys:
            reg_model._properties.pop(del_key, None)