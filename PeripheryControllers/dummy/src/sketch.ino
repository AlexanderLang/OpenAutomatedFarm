#include <EEPROM.h>

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
String fwName = "Dummy";
String fwVersion = "0.1";
const int num_sensors = 2;
OAF_Sensor::Sensor sensors[num_sensors];
const int num_actuators = 2;
OAF_Actuator::Actuator actuators[num_actuators];
int lc = 0;
int lcc = 0;

void setup() {
    // initialize sensors
    sensors[0].name = "Temperature 1";
    sensors[0].unit = "°C";
    sensors[0].precision = 0.1;
    sensors[0].min = 0;
    sensors[0].max = 100;
    sensors[0].offset = get_sensor_offset(0);
    sensors[0].gain = get_sensor_gain(0);

    sensors[1].name = "Temperature 2";
    sensors[1].unit = "°C";
    sensors[1].precision = 0.1;
    sensors[1].min = 0;
    sensors[1].max = 100;
    sensors[1].offset = get_sensor_offset(1);
    sensors[1].gain = get_sensor_gain(1);

    // initialize actuators
    actuators[0].name = "LED";
    actuators[0].unit = "0/1";
    actuators[0].default_value = 0.0;
    actuators[0].pin_number = 13;
    actuators[0].offset = get_actuator_offset(num_sensors, 0);
    actuators[0].gain = get_actuator_gain(num_sensors, 0);

    actuators[1].name = "Fan";
    actuators[1].unit = "%";
    actuators[1].default_value = 0.0;
    actuators[1].pin_number = 3;
    actuators[1].offset = get_actuator_offset(num_sensors, 1);
    actuators[1].gain = get_actuator_gain(num_sensors, 1);

	Serial.begin(OAF_SERIALSHELL_BAUD);
	Serial.println("ready!");
}

void loop() {
	// increment loop counter
	lc++;
	if (lc >= 1000) {
		lc = 0;
		lcc++;
		if (lcc >= 20) {
			lcc = 0;
			for (int i = 0; i < num_sensors; i++) {
				sensors[i].value += 0.01;
				if (sensors[i].value > sensors[i].max) {
					sensors[i].value = sensors[i].min;
				}
			}
		}
	}
	if(actuators[1].value > 0){
    	digitalWrite(13, HIGH);
    } else {
        digitalWrite(13, LOW);
    }
}

/**********************************************************************
 * Serial communication
 * ********************************************************************
 */


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
