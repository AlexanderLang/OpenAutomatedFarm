#include <EEPROM.h>
#include <Wire.h>
#include <avr/wdt.h> 

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
    {"P1", 0.0, 0.0, "1/0"},    //Pump 1
    {"P2", 0.0, 0.0, "1/0"},    //Pump 2
    {"P3", 0.0, 0.0, "1/0"},    //Pump 3
    {"P4", 0.0, 0.0, "1/0"},    //Pump 4
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
long int ph_sum = 0;
float ph_value = 0;

//EC 
int loopcounter_ec = 0;
long int ec_sum = 0;
float ec_value = 0;

//Tanksensor
int loopcounter_tank = 0;
long int tanklevel_sum = 0;
float tanklevel_value = 0;

//Water-Tempsensor
int loopcounter_watertemperature = 0;
long int watertemperature_sum = 0;
float watertemperature_value = 0;

//Water-In-Sensor
int  count_water_in = 0;


float measure_tanklevel() {
  float offset = 39;
  float gain = -0.2;
  int meansteps = 10;
  tanklevel_sum += analogRead(tanklevel_pin);
  loopcounter_tank += 1;
  if(loopcounter_tank > meansteps){
    tanklevel_value = tanklevel_sum * gain / meansteps + offset;
    loopcounter_tank = 0;
    tanklevel_sum = 0;
  }
  return tanklevel_value;
}

float measure_ph() {
  float offset = -3.37;
  float gain = 3.0/148;
  int meansteps = 200;
  ph_sum += analogRead(ph_pin);
  loopcounter_ph+=1;
  if (loopcounter_ph > meansteps) {
    ph_value = ph_sum * gain / meansteps + offset;
    loopcounter_ph = 0;
    ph_sum = 0;
  }
  return ph_value;
}

float measure_ec() {
  float offset = -0.4169;
  float gain = 0.002513;
  int meansteps = 200;
  ec_sum += analogRead(ec_pin);
  loopcounter_ec+=1;
  if (loopcounter_ec > meansteps) {
    ec_value = ec_sum * gain / meansteps + offset;
    loopcounter_ec = 0;
    ec_sum = 0;
  }
  return ec_value;
}

float measure_watertemperature() {
  float offset = 0;
  float gain = 1;
  int meansteps = 1000;
  watertemperature_sum += analogRead(watertemperature_pin);
  loopcounter_watertemperature += 1;
  if (loopcounter_watertemperature > meansteps) {
    watertemperature_value = watertemperature_sum * gain / meansteps + offset;
    loopcounter_watertemperature = 0;
    watertemperature_sum = 0;
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
  analogWrite(circulation_pin, LOW);
  digitalWrite(water_in_pin, LOW);
  digitalWrite(water_out_pin, LOW);
  attachInterrupt(1, count_water_in_pulse, CHANGE);
  
  wdt_enable(WDTO_8S);	
  Serial.println("ready!");
}

void loop() {
  sensors[0].value = measure_ph();
  sensors[1].value = measure_ec();
  sensors[2].value = measure_tanklevel();
  sensors[3].value = measure_watertemperature();

  digitalWrite(pump_1_pin, (int) actuators[0].value);  //Pump 1	
  digitalWrite(pump_2_pin, (int) actuators[1].value);  //Pump 2	
  digitalWrite(pump_3_pin, (int) actuators[2].value);  //Pump 3	
  digitalWrite(pump_4_pin, (int) actuators[3].value);  //Pump 4
  analogWrite(circulation_pin, (int) actuators[4].value);  //Water-Circulation
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
	wdt_reset();
	byte found = 0;
	int index = 0;
	int al = 0;
	byte cmd_error = 0;
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
	            if(index >= al - 1){
	                cmd_error = 1;
	                break;
	            }
	            j++;
	        }
	        if(!cmd_error){
    	        setpoint[j] = '\0';
	            actuators[i].value = atof(setpoint);
	            Serial.print(actuators[i].value);
	            Serial.print(';');
	            index++;
	        } else{
	            Serial.print("Error");
	            break;
	        }
	    }
	    if(index < al -1){
	        Serial.print("Error");
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
