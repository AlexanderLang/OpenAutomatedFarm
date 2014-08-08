#include <EEPROM.h>

#define OAF_SERIALSHELL_BAUD 57600
#define ADDRESS_ID 0

namespace OAF_Sensor {
typedef struct {
	String name;
	float value;
	String unit;
	float precision;
	float samplingTime;
	float min;
	float max;
} Sensor;
}

/**********************************************************************
 * Global variables
 */
String fwName = "Dummy";
String fwVersion = "0.1";
int num_sensors = 6;
OAF_Sensor::Sensor sensors[] = { { "T1", 10.0, "°C", 0.2, 0.5, 0, 100 }, { "T2", 20.0,
		"°C", 0.2, 0.5, 10, 40 }, { "T3", 30.0, "°C", 0.2, 0.5, 10, 40 }, { "H1", 20.0,
		"%", 2.0, 1.0, 20, 95 }, { "H2", 50.0, "%", 2.0, 1.0, 20, 95 }, { "H3", 80.0, "%",
		2.0, 1.0, 20, 95 } };
int lc = 0;
int lcc = 0;

void setup() {
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
}

/**********************************************************************
 * Serial communication
 * ********************************************************************
 */

int com_state = 0;
char com_cmd = 0;
String com_arg = "";

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
		EEPROM.write(ADDRESS_ID, (char) com_arg.toInt());
		Serial.println(EEPROM.read(ADDRESS_ID));
		break;
	case 'l':
		// get sensor list
		for (int i = 0; i < num_sensors; i++) {
			Serial.print(sensors[i].name);
			//Serial.print('\t');
			//Serial.print(sensors[i].value);
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
			if (sensors[i].name == com_arg) {
				Serial.println(sensors[i].value);
				found = 1;
				break;
			}
		}
		if (found == 1) {
			break;
		}
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
			// reset com_state
			com_state = 0;
			// reset com_arg
			com_arg = "";
		} else {
			// read argument
			com_arg += c;
		}
	}
}
