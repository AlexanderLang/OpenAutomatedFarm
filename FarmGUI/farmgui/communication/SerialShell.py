from time import sleep
import serial
import logging


class SerialShell(object):
    """
    classdocs
    """

    def __init__(self, device_name):
        self.device_name = device_name
        self.serial = serial.Serial(device_name,
                                    baudrate=38400,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=0.5,
                                    xonxoff=0,
                                    rtscts=0)
        # Toggle DTR to reset Arduino
        self.serial.setDTR(False)
        sleep(1)
        self.serial.flushInput()
        self.serial.flushOutput()
        self.serial.setDTR(True)
        # wait for "ready!" greeting from arduino 
        self.read_line()

    def get_id(self):
        return int(self.execute_cmd('i'))

    def set_id(self, _id):
        response = self.execute_cmd('I' + str(_id))
        if int(response) != _id:
            # error occurred
            logging.error('SerialShell ' + self.device_name + ': error setting id ('+str(_id)+ ' != '+response+')')

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
        response = self.execute_cmd(cmd)
        return_values = response.split(';')
        return_values.pop()
        # compare response to values (should be equal)
        error = False
        for i in range(len(return_values)):
            if values[i] != float(return_values[i]):
                error = True
        if error is True:
            logging.error('SerialShell' + self.device_name + ': error setting actuator values (res: '+response+')')

    def get_sensor_values(self):
        response = self.execute_cmd('s')
        values = []
        strings = response.split(';')
        strings.pop()
        for val_str in strings:
            values.append(float(val_str))
        return values

    def get_sensor_calibration(self, sensor_number):
        response = self.execute_cmd('C' + str(sensor_number))
        response = response.split(';')
        return {'offset': float(response[0]),
                'gain': float(response[1])}

    def set_sensor_calibration(self, sensor_number, values):
        response = self.execute_cmd('c' + str(sensor_number) + ' ' + str(values['offset']) + ';' + str(values['gain']))
        response = response.split(';')
        if float(response[0]) != values['offset']:
            logging.error('SerialShell: error setting calibration offset')
        if float(response[1]) != values['gain']:
            logging.error('SerialShell: error setting calibration gain')

    def execute_cmd(self, cmd):
        self.serial.write(bytearray(cmd + '\n', 'ascii'))
        line = self.read_line()
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

    def close(self):
        self.serial.close()
