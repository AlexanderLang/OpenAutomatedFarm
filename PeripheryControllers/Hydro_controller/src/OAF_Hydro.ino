#include <EEPROM.h>
#include <Wire.h>

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
String fwName = "Hydro";
String fwVersion = "0.1";
int num_sensors = 4;
OAF_Sensor::Sensor sensors[] = { 
  { "PH", 7.0, "pH", 0.1, 0, 14 },
  { "EC", 0.0, "mS", 0.1, 0, 5000 },
  { "TL", 0.0, "Liter", 0.1, 0, 30 },
  { "T", 20.0, "°C", 0.1, 5, 40 }
};

int num_actuators = 7;
OAF_Actuator::Actuator actuators[] = {
    {"P1", 0.0, 0.0, "%"},    //Pump 1
    {"P2", 0.0, 0.0, "1/0"},  //Pump 2
    {"P3", 0.0, 0.0, "%"},    //Pump 3
    {"P4", 0.0, 0.0, "%"},    //Pump 4
    {"WC", 0.0, 0.0, "%"},    //Water-Circulation
    {"WI", 0.0, 0.0, "1/0"},   //Water IN
    {"WO", 0.0, 0.0, "1/0"}   //Water OUT
};

int lc = 0;
int lcc = 0;

//DI/DO-Pins
int pump_1_pin = 13;
int pump_2_pin = 12;
int pump_3_pin = 11;
int pump_4_pin = 10;
int circulation_pin = 9;
int water_in_pin = 8;
int water_out_pin = 7;
int water_in_sensor = 2;

//AnalogInput-Pins
int ph_pin = 2;
int ec_pin = 1;
int watertemperature_pin = 0;
int tanklevel_pin = 3;

//PH
int loopcounter_ph = 0;
long int ph_value_raw = 0;

//EC 
int loopcounter_ec = 0;
long int ec_value_raw = 0;

//Tanksensor
long int tanklevel_value_raw = 0;

//Water-Tempsensor
int loopcounter_watertemperature = 0;
long int watertemperature_value_raw = 0;

//Water-In-Sensor
int  count_water_in = 0;


float measure_tanklevel() {
  float tanklevel_offset = 2135;
  float tanklevel_gain = -5;
  tanklevel_value_raw = analogRead(tanklevel_pin);
  return tanklevel_value_raw * tanklevel_gain + tanklevel_offset;
}

float measure_ph() {
  double ph_value = 7;
  float ph_offset = 3.37;
  float ph_gain = 3.0/148;
  int ph_meanstep = 1000;
  int loopcounter_ph = 0;
  long int ph_value_raw = 0;
  ph_value_raw += analogRead(ph_pin);
  loopcounter_ph+=1;
  if (loopcounter_ph > ph_meanstep) {
    ph_value = ph_value_raw*ph_gain/ph_meanstep-ph_offset;
    loopcounter_ph = 0;
    ph_value_raw = 0;
  }
  return ph_value;
}

float measure_ec() {
  double ec_value = 0;
  float ec_offset = 0.4169;
  float ec_gain = 0.002513;
  int ec_meanstep = 1000;
  ec_value_raw += analogRead(ec_pin);
  loopcounter_ec+=1;
  if (loopcounter_ec > ec_meanstep) {
    ec_value = ec_value_raw*ec_gain/ec_meanstep-ec_offset;
    loopcounter_ec = 0;
    ec_value_raw = 0;
  }
  return ec_value;
}

float measure_temp() {
  int watertemperature_value = 25;
  float watertemperature_offset = 0;
  float watertemperature_gain = 1;
  int watertemperature_meanstep = 1000;
  watertemperature_value_raw += analogRead(watertemperature_pin);
  loopcounter_watertemperature+=1;
  if (loopcounter_watertemperature > watertemperature_meanstep) {
    watertemperature_value = watertemperature_value_raw*watertemperature_gain/watertemperature_meanstep+watertemperature_offset;
    loopcounter_watertemperature = 0;
    watertemperature_value_raw = 0;
  }
  return watertemperature_value;
}

void count_water_in_pulse() {
  count_water_in ++;
}

void setup() {
  Wire.begin();
  Serial.begin(OAF_SERIALSHELL_BAUD);
  pinMode(pump_1_pin, OUTPUT);
  pinMode(pump_2_pin, OUTPUT);
  pinMode(pump_3_pin, OUTPUT);
  pinMode(pump_4_pin, OUTPUT);
  pinMode(circulation_pin, OUTPUT);
  pinMode(water_in_pin, OUTPUT);
  pinMode(water_out_pin, OUTPUT);
  pinMode(water_in_sensor, INPUT);
  digitalWrite(pump_1_pin, LOW);
  digitalWrite(pump_2_pin, LOW);
  digitalWrite(pump_3_pin, LOW);
  digitalWrite(pump_4_pin, LOW);
  digitalWrite(circulation_pin, LOW);
  digitalWrite(water_in_pin, LOW);
  digitalWrite(water_out_pin, LOW);
  attachInterrupt(1, count_water_in_pulse, CHANGE);	
  Serial.println("ready!");
}

void loop() {
  sensors[0].value = measure_ph();
  sensors[1].value = measure_ec();
  sensors[2].value = measure_tanklevel();
  sensors[3].value = measure_temp();

  digitalWrite(pump_1_pin, (int) actuators[0].value);  //Pump 1	
  digitalWrite(pump_2_pin, (int) actuators[1].value);  //Pump 2	
  digitalWrite(pump_3_pin, (int) actuators[2].value);  //Pump 3	
  digitalWrite(pump_4_pin, (int) actuators[3].value);  //Pump 4
  digitalWrite(circulation_pin, (int) actuators[4].value);  //Water-Circulation
  digitalWrite(water_in_pin, (int) actuators[5].value);  //Water IN valve	
  digitalWrite(water_out_pin, (int) actuators[6].value);  //Water OUT valve	
  	
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
