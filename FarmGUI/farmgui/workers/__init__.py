from .FarmProcess import FarmProcess
from .PeripheryControllerWorker import PeripheryControllerWorker
from .FarmManager import FarmManager


class UnknownFarmProcess(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + ' is not a known farm process'


def process_factory(name, config_uri):
    if name == 'FarmManager':
        return FarmManager(config_uri)
    elif name == 'PeripheryControllerWorker':
        return PeripheryControllerWorker(config_uri)
    else:
        raise UnknownFarmProcess(name)

from .ProcessSupervisor import ProcessSupervisor
from .ProcessMonitor import ProcessMonitor

# exceptions
from .ProcessSupervisor import FarmProcessInitialisationError
from .ProcessMonitor import ProcessMonitorError


def farm_process_generator(config_uri, redis, process_timeout):
    """ Generate supervised farm processes
    :param config_uri: location of config file
    :param redis: connection to redis server
    :param process_timeout: timeout for process initialisation
    """
    for cls in FarmProcess.__subclasses__():
        yield ProcessSupervisor(cls.__name__, config_uri, redis, process_timeout)