#include <Wire.h>
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
String fwName = "LED";
String fwVersion = "0.1";
int num_sensors = 0;
OAF_Sensor::Sensor sensors[] = { 
    
};

int num_actuators = 3;
OAF_Actuator::Actuator actuators[] = {
    {"WH", 0.0, 0.0, "%"},    //White LED
    {"BL", 0.0, 0.0, "%"},  //Blue LED
    {"RE", 0.0, 0.0, "%"},    //Red LED
};

int lc = 0;
int lcc = 0;


//DO-Pins
int white_pwm_pin = 9;
int blue_pwm_pin = 6;
int red1_pwm_pin = 5;
int red2_pwm_pin = 10;


void setup() {
  Wire.begin();	
  Serial.begin(OAF_SERIALSHELL_BAUD);  
  // initialize white
  pinMode(white_pwm_pin, OUTPUT);
  analogWrite(white_pwm_pin, 0);
  // initialize blue
  pinMode(blue_pwm_pin, OUTPUT);
  analogWrite(blue_pwm_pin, 0);
  // initialize red
  pinMode(red1_pwm_pin, OUTPUT);
  analogWrite(red1_pwm_pin, 0);
  pinMode(red2_pwm_pin, OUTPUT);
  analogWrite(red2_pwm_pin, 0);
  
  Serial.println("ready!");
}

void loop() { 
  if ((int) actuators[1].value > 180) {
    actuators[1].value = 180;
  };
  
  analogWrite(white_pwm_pin, (int) actuators[0].value);  //Set white LED
  analogWrite(blue_pwm_pin, (int) actuators[1].value);  //Set blue LED
  analogWrite(red1_pwm_pin, (int) actuators[2].value);  //Set red 1 LED
  analogWrite(red2_pwm_pin, (int) actuators[2].value);  //Set red 2 LED
 
  
  
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
