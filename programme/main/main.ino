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

#include "Adafruit_NeoPixel.h"
#ifdef __AVR__
  #include <avr/power.h>
#endif

// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1
#define PIN            6

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS      20

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
int delayval = 500; // delay for half a second

// #######################################################



SoftwareSerial blueToothSerial(RxD,TxD);

int velo_speed = 0;
int loop_iter = 0;
int last_dcc_iter = -1;

int iter_led = 0;
int mode_led = 0;

unsigned long lastCommunicationTime = 0;
const unsigned long timeoutDuration = 2000;

bool client_connected = false;


void setup(){
    // LED ---------------------------------- 
    // Led exemple :
    // https://wiki.seeedstudio.com/Grove-LED_ring/

    #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) {
        clock_prescale_set(clock_div_1);
    }
    #endif
    
    pixels.setBrightness(255);
    pixels.begin(); // This initializes the NeoPixel library.  

    led_blue();
    
    // BLUETOOTH ------------------------------
    Serial.begin(9600);
    Serial.println("Démarrage en cours");
    pinMode(RxD, INPUT);
    pinMode(TxD, OUTPUT);
    setupBlueToothConnection();


    // ACCELEROMETRE --------------------------
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

    Serial.println("Start figure-8 calibration");
    calibrate(10000);
    Serial.println("");
    
    led_green();
    Serial.println("Calibration ternimé");
    delay(2000);
    led_clean();
}


void loop(){
  loop_iter = loop_iter + 1;
  
  if (last_dcc_iter >= 0) {
    last_dcc_iter += 1;
    mode_led = 1;
  }
  if (last_dcc_iter >= 30) {
    last_dcc_iter = -1;
    mode_led = 0;
  }

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
      // Laisser une variable à envoyer régulièrement pour ping le client
      blueToothSerial.print("speed:");
      blueToothSerial.print(velo_speed);
      blueToothSerial.print('#');
      }
  }
  get_acceleration();
  
  if ( iter_led >= 80 ) { 
        iter_led = 0;
  }
  
  led();
  
  delay(10);
}


// LED ----------------------------------------------

void led() {
  iter_led = iter_led + 1;

  if ( mode_led == 0 ) {
    led_clean();
  }
  else if ( mode_led == 1 ) { 
   led_red();
  }
  else if ( mode_led == 2 ) {
    if(iter_led <= 40 ) {
      led_right();
      led_left();
    } 
    else if ( iter_led >= 40) { 
       led_clean();
    }    
  } 
  
  else if ( mode_led == 3 ) {
    if(iter_led <= 40 ) {
      led_left();
    } 
    else if ( iter_led >= 40) { 
       led_clean();
    }
  }
  else if ( mode_led == 4 ) {
    if(iter_led <= 40 ) {
      led_right();
    } 
    else { 
      led_clean();
    }
  }
}

void led_clean() {
  for (int i = 0; i < 16; i++) {
     pixels.setPixelColor(i, pixels.Color(0, 0, 0)); 
  }  
  pixels.show();
}

void led_red() {
  for (int i = 0; i < 16; i++) {
     pixels.setPixelColor(i, pixels.Color(255, 0, 0)); 
  }  
  pixels.show();
}

void led_left() {
  for (int i = 1; i < 6; i++) {
     pixels.setPixelColor(i, pixels.Color(255, 55, 0)); 
  }  
  pixels.show();
}

void led_right() {
  for (int i = 9; i < 14; i++) {
     pixels.setPixelColor(i, pixels.Color(255, 55, 0)); 
  }  
  pixels.show();
}

void led_green() {
  for (int i = 0; i < 16; i++) {
     pixels.setPixelColor(i, pixels.Color(0, 255, 0)); 
  }  
  pixels.show();
}


void led_blue() {
//  for (int i = 0; i < 16; i++) {
//     pixels.setPixelColor(i, pixels.Color(0, 0, 255)); 
//  }  
//  pixels.show();
  pixels.rainbow(0);
  pixels.show();
}


// ACCELEROMETRE ------------------------------------
int x_moyenne = 0;

void calibrate(uint32_t timeout) {
  uint32_t timeStart = 0;

  int x_values = 0;
  int nb_x_values = 0;
  delay(100);

  timeStart = millis();

  while ((millis() - timeStart) < timeout) {
      x = icm20600.getAccelerationX();

      x_values += x;
      nb_x_values += 1;

      Serial.print(".");
      delay(100);
  }
  x_moyenne = x_values / nb_x_values;
}


void get_acceleration() {
  acc_x = icm20600.getAccelerationX() - x_moyenne;
  if (acc_x < -300) { 
    last_dcc_iter = 0;
  }
}


// BLUETOOTH -----------------------------------------
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
