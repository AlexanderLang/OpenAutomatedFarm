from .Regulator import Regulator
from .RegulatorProperty import RegulatorProperty
from .P import P
from .PI import PI
from .Difference import Difference
from .RootHumidifier import RootHumidifier


def regulator_factory(name):
    return eval(name + "()")


def get_regulator_list():
    names = []
    for reg in Regulator.__subclasses__():
        names.append(reg.__name__)
    return names
