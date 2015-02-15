from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from time import sleep
from datetime import datetime

from farmgui.communication import get_redis_number
from farmgui.workers import process_factory


class FarmProcessInitialisationError(Exception):
    """

    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ProcessSupervisor(object):
    """
    The process supervisor class makes sure a farm process is running properly
    """

    def __init__(self, process_name, config_uri, redis_conn, timeout):
        """ The constructor. It creates the process and starts it.
        :param process_name: name of process that should be started
        :param config_uri: location of the configuration file
        :param redis_conn: redis connection
        :param timeout: process initialisation timeout
        :return:
        """
        self.process_name = process_name
        self.config_uri = config_uri
        self.redis_conn = redis_conn
        self.timeout = timeout
        self.worker = None
        self.restart()

    def wait_for_initialisation(self):
        """
        makes sure the process starts properly
        :return:
        """
        # wait for worker to reset watchdog (i.e. start working)
        start_time = datetime.now()
        while not self.check_watchdog():
            if not self.worker.is_alive():
                # an error occurred
                raise FarmProcessInitialisationError('process died')
            elif (datetime.now() - start_time) > self.timeout:
                # something is taking too long
                raise FarmProcessInitialisationError('initialisation timeout reached')
            sleep(0.25)

    def check_watchdog(self):
        if get_redis_number(self.redis_conn, self.worker.watchdog_key) == 1:
            return True
        return False

    def restart(self):
        if self.worker is not None:
            self.worker.terminate()
            self.worker.join()
        self.worker = process_factory(self.process_name, self.config_uri)
        self.worker.start()
        self.wait_for_initialisation()