#include <SoftwareSerial.h>   //Software Serial Port
#define RxD         10
#define TxD         11

// #######################################################

#include "AK09918.h"
#include "ICM20600.h"
#include <Wire.h>

AK09918_err_type_t err;
int32_t x, y, z;
AK09918 ak09918;
ICM20600 icm20600(true);
int16_t acc_x, acc_y, acc_z;
int32_t offset_x, offset_y, offset_z;
double roll, pitch;
// Find the magnetic declination at your location
// http://www.magnetic-declination.com/
double declination_shenzhen = -2.2;
int x_a=0;


// #######################################################



SoftwareSerial blueToothSerial(RxD,TxD);

int velo_speed = 0;
int loop_iter = 0;

unsigned long lastCommunicationTime = 0;
const unsigned long timeoutDuration = 2000;

bool client_connected = false;


void setup(){
    Serial.begin(9600);
    Serial.println("Démarrage en cours");
    pinMode(RxD, INPUT);
    pinMode(TxD, OUTPUT);
    setupBlueToothConnection();
    Serial.println("Démarrage ternimé");


    // ######################################################
    // join I2C bus (I2Cdev library doesn't do this automatically)
    Wire.begin();

    err = ak09918.initialize();
    icm20600.initialize();
    ak09918.switchMode(AK09918_POWER_DOWN);
    ak09918.switchMode(AK09918_CONTINUOUS_100HZ);
    Serial.begin(9600);

    err = ak09918.isDataReady();
    while (err != AK09918_ERR_OK) {
        Serial.println("Waiting Sensor");
        delay(100);
        err = ak09918.isDataReady();
    }

    Serial.println("Start figure-8 calibration after 2 seconds.");
    delay(2000);
    calibrate(10000, &offset_x, &offset_y, &offset_z);
    Serial.println("");
    
    Serial.println("Calibration ternimé");
}


void loop(){
  loop_iter = loop_iter + 1;

  // Détecter la déconnection
  if (millis() - lastCommunicationTime > timeoutDuration and client_connected) {
    client_connected = false;
    Serial.println("Client bluetooth déconnecté !");
  }

  // Détecter la réception
  String recept = bluetooth_recv();
  if (recept != "") {
    lastCommunicationTime = millis();

    if (recept.endsWith("connected") or recept == "connected") {
      client_connected = true;
      Serial.println("Client bluetooth connecté !");
    } else
    if (recept == "deconnected") {
      client_connected = false;
      Serial.println("Client bluetooth déconnecté !");
    } else
    if (recept != "p") {
      Serial.println(recept);
    }
  }

  // Détecter l'entrée
  if (Serial.available() > 0) {
    String text = Serial.readString();
    blueToothSerial.print("print:");
    blueToothSerial.print(text);
    blueToothSerial.print('#');
  }

  // Envoyer des messages
  if (loop_iter >= 10) {
    loop_iter = 0;
    if (client_connected) {
      get_speed();
      // Laisser une variable à envoyer régulièrement pour ping le client
      blueToothSerial.print("speed:");
      blueToothSerial.print(velo_speed);
      blueToothSerial.print('#');
      }
  }
  
  delay(10);
}


String last_recieve = "";

String bluetooth_recv () {
  byte recu;
  String text = last_recieve;
  while (true) {
    if (blueToothSerial.available()>0) {
      byte recu = blueToothSerial.read();
      char charRecu = static_cast<char>(recu);
      if (charRecu == '#') {
        break;
      } else {
        text = text + charRecu;
      }
    } else {
      last_recieve = text;
      return "";
    }
  }
  last_recieve = "";
  return text;
}


void get_speed() {
  acc_x = icm20600.getAccelerationX();
  Serial.print("A:  ");
  Serial.print(acc_x);
  Serial.print(", ");
  Serial.println(x_a+10);

  if (acc_x<x_a+15) {
    Serial.println("OK");
   
  } else {
    Serial.println("Pas OK");
  }
  int x_a=acc_x;
  velo_speed = acc_x;
}


void calibrate(uint32_t timeout, int32_t* offsetx, int32_t* offsety, int32_t* offsetz) {
    int32_t value_x_min = 0;
    int32_t value_x_max = 0;
    int32_t value_y_min = 0;
    int32_t value_y_max = 0;
    int32_t value_z_min = 0;
    int32_t value_z_max = 0;
    uint32_t timeStart = 0;

    ak09918.getData(&x, &y, &z);

    value_x_min = x;
    value_x_max = x;
    value_y_min = y;
    value_y_max = y;
    value_z_min = z;
    value_z_max = z;
    delay(100);

    timeStart = millis();

    while ((millis() - timeStart) < timeout) {
        ak09918.getData(&x, &y, &z);

        /* Update x-Axis max/min value */
        if (value_x_min > x) {
            value_x_min = x;
            // Serial.print("Update value_x_min: ");
            // Serial.println(value_x_min);

        } else if (value_x_max < x) {
            value_x_max = x;
            // Serial.print("update value_x_max: ");
            // Serial.println(value_x_max);
        }

        /* Update y-Axis max/min value */
        if (value_y_min > y) {
            value_y_min = y;
            // Serial.print("Update value_y_min: ");
            // Serial.println(value_y_min);

        } else if (value_y_max < y) {
            value_y_max = y;
            // Serial.print("update value_y_max: ");
            // Serial.println(value_y_max);
        }

        /* Update z-Axis max/min value */
        if (value_z_min > z) {
            value_z_min = z;
            // Serial.print("Update value_z_min: ");
            // Serial.println(value_z_min);

        } else if (value_z_max < z) {
            value_z_max = z;
            // Serial.print("update value_z_max: ");
            // Serial.println(value_z_max);
        }

        Serial.print(".");
        delay(100);

    }

    *offsetx = value_x_min + (value_x_max - value_x_min) / 2;
    *offsety = value_y_min + (value_y_max - value_y_min) / 2;
    *offsetz = value_z_min + (value_z_max - value_z_min) / 2;
}


void setupBlueToothConnection(){
  blueToothSerial.begin(9600);  
  blueToothSerial.print("AT");
  delay(400);
  blueToothSerial.print("AT+DEFAULT");             // Restore all setup value to factory setup
  delay(2000);
  blueToothSerial.print("AT+NAMESafe_Cycling");    // set the bluetooth name as "Safe_Cycling"
  delay(400);
  blueToothSerial.print("AT+PIN1234");             // set the pair code to connect
  delay(400);
  blueToothSerial.print("AT+AUTH1");            
  delay(400);
  blueToothSerial.flush();
}
