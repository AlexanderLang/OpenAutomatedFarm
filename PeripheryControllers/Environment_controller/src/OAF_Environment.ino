#include <EEPROM.h>
#include <Wire.h>
#include <SHT2x.h>
#include <JeeLib.h>
#include <PortsSHT21.h>

#define OAF_SERIALSHELL_BAUD 38400
#define ADDRESS_ID 0


void EEPROM_writeFloat(int ee, const float& value)
{
    const byte* p = (const byte*)(const void*)&value;
    int i;
    for (i = 0; i < 4; i++) {
        EEPROM.write(ee++, *p++);
    }
}

float EEPROM_readFloat(int ee)
{
    float ret;
    byte* p = (byte*)(void*)&ret;
    int i;
    for (i = 0; i < 4; i++) {
        *p++ = EEPROM.read(ee++);
    }
    return ret;
}

namespace OAF_Sensor {
typedef struct {
	String name;
	float value;
	String unit;
	float precision;
	float min;
	float max;
	float offset;
	float gain;
} Sensor;
}

namespace OAF_Actuator {
typedef struct {
    String name;
    float value;
    float default_value;
    String unit;
    int pin_number;
    int offset;
    float gain;
} Actuator;
}

void calculate_sensor_value(OAF_Sensor::Sensor *sensor, float value){
    sensor->value = sensor->offset + value * sensor->gain;
}

int sensor_offset_address(int sensor_number){
    return 1 + 8 * sensor_number;
}

int sensor_gain_address(int sensor_number){
    return 5 + 8 * sensor_number;
}

int actuator_offset_address(int number_sensors, int actuator_number){
    return 1 + (8 * number_sensors) + (8 * actuator_number);
}

int actuator_gain_address(int number_sensors, int actuator_number){
    return 5 + (8 * number_sensors) + (8 * actuator_number);
}

float get_sensor_offset(int sensor_number){
    return EEPROM_readFloat(sensor_offset_address(sensor_number));
}

float get_sensor_gain(int sensor_number){
    return EEPROM_readFloat(sensor_gain_address(sensor_number));
}

float get_actuator_offset(int number_sensors, int actuator_number){
    return EEPROM_readFloat(actuator_offset_address(number_sensors, actuator_number));
}

float get_actuator_gain(int number_sensors, int actuator_number){
    return EEPROM_readFloat(actuator_gain_address(number_sensors, actuator_number));
}

void set_sensor_offset(int sensor_number, float value){
    return EEPROM_writeFloat(sensor_offset_address(sensor_number), value);
}

void set_sensor_gain(int sensor_number, float value){
    return EEPROM_writeFloat(sensor_gain_address(sensor_number), value);
}

void set_actuator_offset(int number_sensors, int actuator_number, float value){
    return EEPROM_writeFloat(actuator_offset_address(number_sensors, actuator_number), value);
}

void set_actuator_gain(int number_sensors, int actuator_number, float value){
    return EEPROM_writeFloat(actuator_gain_address(number_sensors, actuator_number), value);
}

/**********************************************************************
 * Global variables
 */
String fwName = "Environment";
String fwVersion = "0.1";
int num_sensors = 4;
OAF_Sensor::Sensor sensors[] = { 
    { "TI", 20.0, "°C", 0.2, 5, 40 }, //Growarea Temperature
    { "TO", 20.0, "°C", 0.2, 5, 40 }, //Outside Temperature
    { "HI", 50, "%", 2.0, 0, 100 },   //Growarea Humidity
    { "HO", 50,	"%", 2.0, 0, 100 }    //Outside Humidity
};

int num_actuators = 6;
OAF_Actuator::Actuator actuators[] = {
    {"EX", 0.0, 0.0, "%"},    //Exhaust
    {"FO", 0.0, 0.0, "1/0"},  //Fog
    {"RF", 0.0, 0.0, "%"},    //Rootfan
    {"AC", 0.0, 0.0, "%"},    //Aircirculation
    {"CF", 0.0, 0.0, "%"},    //CT-Circulation
    {"CP", 0.0, 0.0, "1/0"}   //CT-Pump
};

int lc = 0;
int lcc = 0;

//SHT softTWI
SHT21 hsensor1 (1);
float humO, tempO;

//DO-Pins
int ex = 8;
int fo = 11;
int rf = 10;
int ac = 9;
int cf = 6;
int cp = 4;


void setup() {
  Wire.begin();	
  Serial.begin(OAF_SERIALSHELL_BAUD);
  pinMode(ex, OUTPUT);
  analogWrite(ex, 0);
  pinMode(fo, OUTPUT);
  digitalWrite(fo, LOW);
  pinMode(rf,OUTPUT);
  analogWrite(rf, 0); 
  pinMode(ac, OUTPUT);
  analogWrite(ac, 0); 
  pinMode(cf, OUTPUT);
  analogWrite(cf, 0);
  pinMode(cp, OUTPUT);   
  digitalWrite(cp, LOW);
  
  // Timer settings
  TCCR2A = _BV(COM2A1) | _BV(COM2B1) | _BV(WGM21) | _BV(WGM20);
  TCCR1A = _BV(COM1A1) | _BV(COM1B1) | _BV(WGM10);
  TCCR2B = TCCR2B & 0b11111000 | 0x01;
  TCCR1B = TCCR1B & 0b11111000 | 0x01;
  
  Serial.println("ready!");
}

void loop() {
  hsensor1.measure(SHT21::HUMI);
  hsensor1.measure(SHT21::TEMP);
  hsensor1.calculate(humO, tempO);
  sensors[0].value = SHT2x.GetTemperature();
  sensors[1].value = tempO;
  sensors[2].value = SHT2x.GetHumidity();
  sensors[3].value = humO;
  
  analogWrite(ex, (int) actuators[0].value);  //Set Exhaust
  digitalWrite(fo, (int) actuators[1].value);  //Set Fog
  analogWrite(rf, (int) actuators[2].value);  //Set Rootfan
  analogWrite(ac, (int) actuators[3].value);  //Set Aircirculation
  analogWrite(ex, (int) actuators[4].value);  //Set CT-Fan  
  digitalWrite(cp, (int) actuators[5].value); //Set CT-Pump
  
  
}

/**********************************************************************
 * Serial communication
 * ********************************************************************
 */

int com_state = 0;
char com_cmd = 0;
String com_arg1 = "";
String com_arg2 = "";

void execute_cmd(char cmd) {
	byte found = 0;
	int index = 0;
	int al = 0;
	// look for commands
	switch (cmd) {
	case 'f':
		// get firmware name
		Serial.println(fwName);
		break;
	case 'v':
		// get firmware version
		Serial.println(fwVersion);
		break;
	case 'i':
		// get ID
		Serial.println(EEPROM.read(ADDRESS_ID));
		break;
	case 'I':
		// set ID
		EEPROM.write(ADDRESS_ID, (char) com_arg1.toInt());
		Serial.println(EEPROM.read(ADDRESS_ID));
		break;
	case 'S':
		// get sensor list
		for (int i = 0; i < num_sensors; i++) {
			Serial.print(sensors[i].name);
			Serial.print(';');
			Serial.print(sensors[i].unit);
			Serial.print(';');
			Serial.print(sensors[i].precision);
			Serial.print(';');
			Serial.print(sensors[i].min);
			Serial.print(';');
			Serial.print(sensors[i].max);
			Serial.print('|');
		}
		Serial.println();
		break;
	case 's':
		// read sensors
		for (int i = 0; i < num_sensors; i++) {
			Serial.print(sensors[i].value);
			Serial.print(';');
		}
		Serial.println();
	    break;
	case 'C':
	    // get sensor calibration
	    {
	        char buffer[3];
	        com_arg1.toCharArray(buffer, 3);
	        index = atoi(buffer);
    	    Serial.print(sensors[index].offset);
	        Serial.print(';');
	        Serial.print(sensors[index].gain);
    	    Serial.println();
    	}
	    break;
	case 'c':
	    // set sensor calibration
	    {
	        char buffer[3];
	        com_arg1.toCharArray(buffer, 3);
	        index = atoi(buffer);
	        al = com_arg2.length() + 1;
	        char carray[al];
	        com_arg2.toCharArray(carray, al);
	        char data[al];
	        int i = 0;
	        int j = 0;
	        while(carray[i] != ';'){
	            data[j] = carray[i];
	            i++;
	            j++;
	        }
	        data[j] = '\0';
	        sensors[index].offset = atof(data);
	        set_sensor_offset(index, sensors[index].offset);
	        Serial.print(sensors[index].offset);
	        Serial.print(';');
	        i++;
	        j = 0;
	        while(carray[i] != ';'){
	            data[j] = carray[i];
	            i++;
	            j++;
	        }
	        data[j] = '\0';
	        sensors[index].gain = atof(data);
	        set_sensor_gain(index, sensors[index].gain);
	        Serial.print(sensors[index].gain);
	        Serial.println();
	    }
        break;
	case 'A':
	    // get actuator list
	    for (int i = 0; i < num_actuators; i++) {
	        Serial.print(actuators[i].name);
	        Serial.print(';');
	        Serial.print(actuators[i].unit);
	        Serial.print(';');
	        Serial.print(actuators[i].default_value);
	        Serial.print('|');
	    }
	    Serial.println();
	    break;
	case 'a':
	    // set actuators
	    {
	    al = com_arg1.length() + 1;
	    char carray[al];
	    char setpoint[al];
	    com_arg1.toCharArray(carray, al);
	    for (int i = 0; i < num_actuators; i++) {
	        int j = 0;
	        while(carray[index] != ';'){
	            setpoint[j] = carray[index];
	            index++;
	            j++;
	        }
	        setpoint[j] = '\0';
	        actuators[i].value = atof(setpoint);
	        Serial.print(actuators[i].value);
	        Serial.print(';');
	        index++;
	    }
	    Serial.println();
	    }
	    break;
	default:
		Serial.println("Error");
	}
	// reset com_state
	com_state = 0;
	// reset com_args
	com_arg1 = "";
	com_arg2 = "";
}

void serialEvent() {
    while (Serial.available()) {
    	char c = (char) Serial.read();
	    switch (com_state) {
    	case 0:
	    	// read command
		    com_cmd = c;
    		com_state++;
	    	break;
    	case 1:
	    	// read argument
		    if (c == '\n') {
			    // input finished, execute
    			execute_cmd(com_cmd);
	    	} else if (c == ' ') {
		        // next argument starts
		        com_state++;
    		} else {
	    		// read argument
		    	com_arg1 += c;
    		}
	    	break;
    	case 2:
	        // read second argument
	        if (c == '\n') {
	            // input finished, execute
    	        execute_cmd(com_cmd);
	        } else {
	            // read argument
	            com_arg2 += c;
    	    }
	    }
	}
}
