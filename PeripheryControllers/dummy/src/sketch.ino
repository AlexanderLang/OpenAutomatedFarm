#include <EEPROM.h>

#define OAF_SERIALSHELL_BAUD 57600
#define ADDRESS_ID 0

namespace OAF_Sensor {
typedef struct {
	String name;
	float value;
	String unit;
	float precision;
	float min;
	float max;
} Sensor;
}

namespace OAF_Actuator {
typedef struct {
    String name;
    float value;
    float default_value;
    String unit;
} Actuator;
}

/**********************************************************************
 * Global variables
 */
String fwName = "Dummy";
String fwVersion = "0.1";
int num_sensors = 6;
OAF_Sensor::Sensor sensors[] = {
    { "T1", 10.0, "°C", 0.2, 0, 100 },
    { "T2", 20.0, "°C", 0.2, 10, 40 },
    { "T3", 30.0, "°C", 0.2, 10, 40 },
    { "H1", 20.0, "%", 2.0, 20, 95 },
    { "H2", 50.0, "%", 2.0, 20, 95 },
    { "H3", 80.0, "%", 2.0, 20, 95 }
};
int num_actuators = 2;
OAF_Actuator::Actuator actuators[] = {
    {"L1", 0.0, 0.0, "%"},
    {"B1", 0.0, 0.0, "1/0"}
};
int lc = 0;
int lcc = 0;

void setup() {
    pinMode(13, OUTPUT);
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
	        index++;
	    }
	    Serial.println(0);
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
