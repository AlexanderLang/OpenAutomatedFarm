#include <EEPROM.h>
#include <Wire.h>
#include <SHT2x.h>
#include <JeeLib.h>
#include <PortsSHT21.h>

#define OAF_SERIALSHELL_BAUD 57600
#define ADDRESS_ID 0

namespace OAF_Sensor {
typedef struct {
	String name;
	float value;
	String unit;
	float samplingTime;
        float precision;
	float min;
	float max;
} Sensor;
}

namespace OAF_Actuator {
typedef struct {
    String name;
    float value;
    String unit;
} Actuator;
}

/**********************************************************************
 * Global variables
 */
String fwName = "Environment";
String fwVersion = "0.1";
int num_sensors = 4;
OAF_Sensor::Sensor sensors[] = { 
    { "TI", 20.0, "°C", 0.2, 2, 5, 40 }, //Growarea Temperature
    { "TO", 20.0, "°C", 0.2, 2, 5, 40 }, //Outside Temperature
    { "HI", 50, "%", 2.0, 2, 0, 100 },   //Growarea Humidity
    { "HO", 50,	"%", 2.0, 2, 0, 100 }    //Outside Humidity
};

int num_actuators = 6;
OAF_Actuator::Actuator actuators[] = {
    {"EX", 0.0, "%"},    //Exhaust
    {"FO", 0.0, "1/0"},  //Fog
    {"RF", 0.0, "%"},    //Rootfan
    {"AC", 0.0, "%"},    //Aircirculation
    {"CF", 0.0, "%"},    //CT-Circulation
    {"CP", 0.0, "1/0"}   //CT-Pump
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
  pinMode(fo, OUTPUT);
  pinMode(rf,OUTPUT); 
  pinMode(ac, OUTPUT); 
  pinMode(cf, OUTPUT); 
  pinMode(cp, OUTPUT); 
  
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
			Serial.print(sensors[i].samplingTime);
			Serial.print(';');
			Serial.print(sensors[i].min);
			Serial.print(';');
                        Serial.print(sensors[i].max);
			Serial.print('|');
		}
		Serial.println();
		break;
	case 's':
		// read sensor named arg
		for (int i = 0; i < num_sensors; i++) {
			if (sensors[i].name == com_arg1) {
				Serial.println(sensors[i].value);
				found = 1;
				break;
			}
		}
		if (found == 0) {
                    Serial.println("Sensor Name Error");
                }
		break;
	case 'A':
      	      // get actuator list
      	        for (int i = 0; i < num_actuators; i++) {
      	            Serial.print(actuators[i].name);
      	            Serial.print(';');
      	            Serial.print(actuators[i].unit);
                    Serial.print('|');
                }
                Serial.println();
      	        break;
	case 'a':
	    // set actuator named arg1 to value arg2
	        for (int i = 0; i < num_actuators; i++) {
	            if (actuators[i].name == com_arg1) {
	                int al = com_arg2.length() + 1;
       	                char carray[al];
	                com_arg2.toCharArray(carray, al);
	                actuators[i].value = atof(carray);
	                Serial.println(actuators[i].value);
	                found = 1;
	                break;
	            }
	        }
	        if (found == 0) {
	            Serial.println("Actuator Name Error");
	        }
	        break;

		
	default:
		Serial.println("Error");
	}
}

void serialEvent() {
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
