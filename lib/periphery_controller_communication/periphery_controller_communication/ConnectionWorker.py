from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
from datetime import datetime

from redis import Redis
redis_conn = Redis('localhost', 6379)

from .SerialShell import SerialShell

class ConnectionWorker(object):
    '''
    classdocs
    '''
    
    def __init__(self, devicename, redis_conn):
        self.redis_conn = redis_conn
        # connect with serial port
        self.serial = SerialShell(devicename)
        controller_id = self.serial.get_id()
        self.channel_name = 'periphery_controller_' + str(controller_id)
        # create command queue
        self.pubsub = redis_conn.pubsub(ignore_subscribe_messages=False)
        self.pubsub.subscribe(self.channel_name)
        # publish presence of new controller
        data = {}
        data['id'] = controller_id
        data['active'] = True
        data['channel'] = self.channel_name
        if controller_id == 0:
            # new controller
            data['fwName'] = self.serial.get_firmware_name()
            data['fwVersion'] = self.serial.get_firmware_version()
            data['sensors'] = self.serial.get_sensors()
        self.redis_conn.publish('controller_connections', data)
    
    def publish_removal(self):
        self.redis_conn.publish('controller_connections', {'id': self.serial.get_id(), 'active': False})
        self.pubsub.close()
    
    def work(self):
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                #print('got data: ' + str(data))
                result = self.serial.execute_cmd(data['cmd'])
                if data['result_channel'] is not None:
                    response = {}
                    response['caller_id'] = data['caller_id']
                    response['time'] = str(datetime.now())
                    response['value'] = result
                    self.redis_conn.publish(data['result_channel'], response)
                    print('oaf_cw: ' + data['result_channel'] + '(' + data['cmd'] + ': ' + result + ')')


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <dev_name>\n'
          '(example: "%s /dev/ttyACM0")' % (cmd, cmd))
    sys.exit(1)
    
def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    dev_name = argv[1]
    worker = ConnectionWorker(dev_name, redis_conn)
    try:
        worker.work()
    finally:
        worker.publish_removal()