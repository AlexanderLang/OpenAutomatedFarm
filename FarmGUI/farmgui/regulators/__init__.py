from .Regulator import Regulator
from .RegulatorProperty import RegulatorProperty
from .P import P
from .PI import PI
from .Difference import Difference
from .RootHumidifier import RootHumidifier
from .HysteresisController import HysteresisController


class UnknownRegulator(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + ' is not a known regulator class'


def regulator_factory(name):
    if name == 'P':
        return P()
    elif name == 'PI':
        return PI()
    elif name == 'Difference':
        return Difference()
    elif name == 'RootHumidifier':
        return RootHumidifier()
    elif name == 'HysteresisController':
        return HysteresisController()
    else:
        raise UnknownRegulator(name)


def get_regulator_list():
    names = []
    for reg in Regulator.__subclasses__():
        names.append(reg.__name__)
    return names
