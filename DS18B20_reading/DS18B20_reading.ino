#include <OneWire.h>

OneWire myWire(5);

bool init = 1;
bool Scratchpad = 1;

String received_string;
int16_t reps;
int16_t measTime;

byte sensor_ID[8];
byte ID_6_bit;

byte data[9];
float celsius;

int16_t count = 0;

unsigned long reftime = 0;
unsigned long millis_time;


void setup() {

  Serial.begin(9600);
  Serial.setTimeout(1);
  pinMode(LED_BUILTIN, OUTPUT);
}


  String EndTask = "End of task";
  String LogTime = "Log the time";
  String EndMesage = "End of mesage";


void loop() {

  if (init) {

    while (!Serial.available()) {
      delay(100);
    }

    // Receives the wanted runtime of the program from user, and checks to se if it is the corect data.

    while (Serial.available()) {

      received_string = Serial.readString();

      if (received_string.substring(0, 5) == "SMFST") {

        reps = received_string.substring(5).toInt();
      }
      else {

        reps = 0;
        EndTask = "Error";
        EndMesage = "Error";
      }
    }

    while (!Serial.available()) {
      delay(100);
    }

    // Recieves the wanted number of measurements per minnute from user, and checks to se if it is the corect data.

    while (Serial.available()) {

      received_string = Serial.readString();

      if (received_string.substring(0, 5) == "SMLST") {

        measTime = received_string.substring(5).toInt();
      }
      else {

        measTime = 0;
        EndTask = "Error";
        EndMesage = "Error";
      }
    }

    // Calculates total number of measurements and time between each measurement

    reps = reps * measTime;
    measTime = measTime * 60000 / reps;

    Serial.println(EndTask);                       // Writes the message that will end the program
    Serial.println(LogTime);                       // Writes the message that logs the time
    Serial.println(EndMesage);                     // Writes the message that will start the next data transfer

    init = 0;
  }

  millis_time = millis();
  digitalWrite(LED_BUILTIN, HIGH);

  // Tells the sensors to loade the curent temperature to scratchpad

  if (Scratchpad) {

    setSratchpad();
  }

  // Checks if the program has reached the total number of measurements and sends end-line to stopp the program

  else if (count >= reps) {

    Serial.println(EndTask);

    init = 1;
    count = 0;

    digitalWrite(LED_BUILTIN, LOW);
  }

  // Serches for sensors to read
  // If there are no more sensors it restarts the reading process and waits for the next measurement

  else {

    if ( !myWire.search(sensor_ID)) {

      myWire.reset_search();
      count = count + 1;
      Scratchpad = 1;

      while ((millis_time - reftime) < measTime) {
        millis_time = millis();
        digitalWrite(LED_BUILTIN, LOW);
      }

      reftime = millis_time;

      return;
    }

    // Reading 6 bits of the second byte in the ID as the 6 bit ID

    ID_6_bit = sensor_ID[1] & 0b00111111;

    // Reads the data from the sensors

    readData();
    
    // Calculates the temperature in celsius

    tempCalculation();

    // Prints all the wanted data

    printData();

    // Sends a mesage to tell the Python program that the curent transmition is finished

    Serial.println(EndMesage);
  }
}


void setSratchpad() {

  if (!myWire.search(sensor_ID)) {

    Scratchpad = 0;
    myWire.reset_search();
    Serial.println(LogTime);                // Sends message to log the time
    delay(1000);                            // This delay is necessary for the sensors to log the curent temperature
  }
  else {

    myWire.reset();
    myWire.select(sensor_ID);
    myWire.write(0x44);                     // Telling the sensor to begin a temperature convertion
  }
}

//----Funktion for reading data from sensors------------------------------------------//

void readData() {

  int i;

  myWire.reset();
  myWire.select(sensor_ID);
  myWire.write(0xBE);             // Comand for opening scratchpad

  for ( i = 0; i < 9; i++) {      // Reading 9 bytes of data from scratchpad
    data[i] = myWire.read();
  }
}


// ----Funkton for calkulating celsius-------------------------------------------------------------------------------//

void tempCalculation() {

  int16_t raw;
  byte config_reg;

  raw = (data[1] << 8) | data[0];                 // Sorting databytes in the right order
  config_reg = (data[4] & 0x60);                  // Reading temperatureresolution from sensor

  if (config_reg == 0x00) raw = raw & ~7;         // 9 bit resolution, 93.75 ms
  else if (config_reg == 0x20) raw = raw & ~3;    // 10 bit res, 187.5 ms
  else if (config_reg == 0x40) raw = raw & ~1;    // 11 bit res, 375 ms
                                                  // default is 12 bit resolution, 750 ms conversion time
  celsius = (float)raw / 16.0;
}


// ----Funktion for printing mesages ------------------------------------------------------------------------------//

void printData() {

  int i;

  for ( i = 0; i < 8; i++) {             // Printing all 8 bytes of sensor ID in HEX
    if (sensor_ID[i] < 16) {
      Serial.print("0");
    }
    Serial.print(sensor_ID[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  Serial.println(ID_6_bit);              // Printing the 6 bit ID of the sensor in numbers

  for ( i = 0; i < 9; i++) {             // Printing all 9 bytes of data from skratchpad in HEX
    if (data[i] < 16) {
      Serial.print("0");
    }
    Serial.print(data[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  Serial.println(celsius, 4);            // Printing calkulated temperature in celsius
}
