import serial
import logging
import time


class SerialShell(object):
    """
    classdocs
    """

    def __init__(self, devicename):
        self.serial = serial.Serial(devicename, 57600)
        self.serial.flushInput()
        self.serial.flushOutput()
        # wait for "ready!" greeting from arduino 
        self.read_line()

    def get_id(self):
        return int(self.execute_cmd('i'))

    def set_id(self, _id):
        self.execute_cmd('I' + str(_id))

    def get_firmware_name(self):
        return self.execute_cmd('f')

    def get_firmware_version(self):
        return self.execute_cmd('v')

    def get_sensors(self):
        sensor_list_string = self.execute_cmd('S').split('|')
        sensor_list_string.pop()
        sensors = []
        for sensorString in sensor_list_string:
            values = sensorString.split(';')
            sensor_dict = {'name': values[0],
                           'unit': values[1],
                           'precision': float(values[2]),
                           'min': float(values[3]),
                           'max': float(values[4])}
            sensors.append(sensor_dict)
        return sensors

    def get_actuators(self):
        actuator_list_string = self.execute_cmd('A').split('|')
        actuator_list_string.pop()
        actuators = []
        for actuator_string in actuator_list_string:
            values = actuator_string.split(';')
            actuator_dict = {'name': values[0],
                             'unit': values[1],
                             'default': values[2]}
            actuators.append(actuator_dict)
        return actuators

    def set_actuator_values(self, values):
        cmd = 'a'
        for val in values:
            cmd += str(val) + ';'
        return self.execute_cmd(cmd)

    def get_sensor_values(self):
        response = self.execute_cmd('s')
        values = []
        strings = response.split(';')
        strings.pop()
        for val_str in strings:
            values.append(float(val_str))
        return values

    def execute_cmd(self, cmd):
        start = time.time()
        self.serial.write(bytearray(cmd + '\n', 'ascii'))
        line = self.read_line()
        logging.debug('SerialShell: executed \"' + cmd + '\" in ' + str(time.time()-start) + ' [s]')
        return line

    def read_line(self):
        line = ''
        tmp = ''
        while True:
            try:
                tmp = self.serial.read(1)
                c = tmp.decode()
            except UnicodeDecodeError:
                tmp = tmp + self.serial.read(1)
                c = tmp.decode()

            if c == '\r':
                self.serial.read(1)
                break
            else:
                line += c
        return line