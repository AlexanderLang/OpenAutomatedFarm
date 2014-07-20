import serial

class SerialShell(object):
    '''
    classdocs
    '''
    
    def __init__(self, devicename):
        self.serial = serial.Serial(devicename, 57600)
        self.serial.flushInput()
        self.serial.flushOutput()
        # wait for "ready!" greeting from arduino 
        self.readLine()
    
    def get_id(self):
        return int(self.execute_cmd('i'))
    
    def set_id(self, _id):
        self.execute_cmd('I'+str(_id))
    
    def get_firmware_name(self):
        return self.execute_cmd('f')
    
    def get_firmware_version(self):
        return self.execute_cmd('v')

    def get_sensors(self):
        sensorListString = self.execute_cmd('l').split('|')
        sensorListString.pop()
        sensors = []
        for sensorString in sensorListString:
            values = sensorString.split(';')
            sensorDict = {}
            sensorDict['name'] = values[0]
            sensorDict['unit'] = values[1]
            sensorDict['samplingTime'] = float(values[2])
            sensors.append(sensorDict)
        return sensors
    
    def get_sensor_value(self, name):
        return float(self.execute_cmd('s'+name))
        

    def execute_cmd(self, cmd):
        self.serial.write(bytearray(cmd + '\n', 'ascii'))
        return self.readLine()
        
    def readLine(self):
        line = ''
        while(True):
            try:
                tmp = self.serial.read(1)
                c = tmp.decode()
            except UnicodeDecodeError:
                tmp = tmp+self.serial.read(1)
                c = tmp.decode()
                
            if(c == '\r'):
                self.serial.read(1)
                break
            else:
                line += c
        self.status = 0
        #print('recived: \"' + line + '\"')
        return line