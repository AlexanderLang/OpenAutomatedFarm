
import psutil

__author__ = 'alex'

_MB_DIV = float(2 ** 20)


class ProcessMonitorError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ProcessMonitor(object):
    """

    """

    def __init__(self, pid, name, redis_conn, timeout):
        self.name = name
        self.redis_conn = redis_conn
        self.timeout = timeout
        self.monitor = psutil.Process(pid)
        self.cpu = 0
        self.mem = 0
        self.update()

    def update(self):
        if not self.monitor.is_running():
            raise ProcessMonitorError('{} is not running anymore'.format(self.name))
        self.cpu = self.monitor.get_cpu_percent()
        self.mem = self.monitor.get_memory_info()[0] / _MB_DIV
        # publish values on redis
        self.redis_conn.setex(self.name + '-cpu', self.cpu, self.timeout)
        self.redis_conn.setex(self.name + '-mem', '%.2f' % self.mem, self.timeout)

    def change_pid(self, pid):
        self.monitor = psutil.Process(pid)
