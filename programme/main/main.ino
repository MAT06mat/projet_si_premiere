// ================================================
//                      INIT
// ================================================

// -------------------- LED --------------------

#include "Adafruit_NeoPixel.h"
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define PIN            6

#define NUMPIXELS      16

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
int delayval = 500; // delay for half a second





// -------------------- ACCELEROMETRE --------------------

#include "ICM20600.h"
#include <Wire.h>

int x;
ICM20600 icm20600(true);


// -------------------- BLUETOOTH --------------------

#include <SoftwareSerial.h>   //Software Serial Port
#define RxD         10
#define TxD         11

SoftwareSerial blueToothSerial(RxD,TxD);
bool client_connected = false;

unsigned long lastCommunicationTime = 0;
const unsigned long timeoutDuration = 2000;


// -------------------- OTHER --------------------

bool left = false;
bool right = false;
bool dcc = false;
int mode = 0;
//  mode :
//     0 -> Rainbow
//     1 -> Pulse
//     2 -> Pulse
//     3 -> Pulse

int loop_iter = 0;
int last_dcc_iter = -1;
int iter_led = 0;




// ================================================
//                     SETUP
// ================================================


void setup(){
    Serial.begin(9600);
    Serial.println("Démarrage en cours");
    
    // -------------------- LED --------------------
    // Led exemple :
    // https://wiki.seeedstudio.com/Grove-LED_ring/
    #if defined (__AVR_ATtiny85__)
    if (F_CPU == 16000000) {
        clock_prescale_set(clock_div_1);
    }
    #endif
    
    pixels.setBrightness(10);
    pixels.begin(); // This initializes the NeoPixel library.  


    // -------------------- ACCELEROMETRE --------------------
    Wire.begin();
    icm20600.initialize();

    Serial.println("Start figure-8 calibration");
    calibrate(5000);
    Serial.println("");
    // Set all Led to green
    led_show(0, 16, 0, 255, 0);
    Serial.println("Calibration ternimé");
    delay(2000);
    led_clean();
    
    // -------------------- BLUETOOTH --------------------
    pinMode(RxD, INPUT);
    pinMode(TxD, OUTPUT);
    setupBlueToothConnection();
}




// ================================================
//                   MAIN LOOP
// ================================================


void loop(){
  loop_iter = loop_iter + 1;

  // Update last dcc iter loop
  if (last_dcc_iter >= 0) {
    last_dcc_iter += 1;
  }
  // Reset last dcc iter loop
  if (last_dcc_iter >= 30) {
    last_dcc_iter = -1;
  }

  // Détecter la déconnection
  if (millis() - lastCommunicationTime > timeoutDuration and client_connected) {
    Serial.println("BlueTooth TimeOut");
    disconnect();
  }

  // Détecter la réception
  String recept = bluetooth_recv();
  if (recept != "") {
    lastCommunicationTime = millis();
    Serial.println(recept);

    if (recept.endsWith("c") or recept == "c") {
      Serial.println("App Signal");
      connect();
    } else if (test(recept, "d")) {
      Serial.println("App Signal");
      disconnect();
    } else if (test(recept, "s_r")) {
      right = false;
    } else if (test(recept, "r")) {
      left = false;
      right = true;
      iter_led = 0;
    } else if (test(recept, "s_l")) {
      left = false;
    } else if (test(recept, "l")) {
      right = false;
      left = true;
      iter_led = 0;
    } else if (test(recept, "s_stop")) {
      dcc = false;
    } else if (test(recept, "stop")) {
      dcc = true;
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
  if (loop_iter >= 100) {
    loop_iter = 0;
    // Laisser une variable à envoyer régulièrement pour ping le client
    blueToothSerial.print("speed:");
    blueToothSerial.print(last_dcc_iter);
    blueToothSerial.print('#');
  }
  get_acceleration();
  if ( iter_led >= 80 ) { 
    iter_led = 0;
  }
  led();
  delay(10);
}


// ================================================
//                 OTHER FUNCTIONS
// ================================================


// -------------------- LED --------------------

void led() {
  iter_led = iter_led + 1;

  // Reset all Led
  led_clean();

  if ( last_dcc_iter >= 0 or dcc) {
   // Set all Led to red 
   led_show(0, 16, 255, 0, 0);
  }
  else if (right) {
    if(iter_led <= 40 ) {
      // Set right Led to orange
      led_show(9, 14, 255, 55, 0);
    }  
  } 
  else if (left) {
    if(iter_led <= 40 ) {
      // Set left Led to orange
      led_show(1, 6, 255, 55, 0);
    } 
  }
}

void led_clean() {
  pixels.clear();
  pixels.show();
}

void led_show(int led_start, int led_finish, int r, int g, int b) {
  for (int i = led_start; i < led_finish; i++) {
     pixels.setPixelColor(i, pixels.Color(r, g, b)); 
  }  
  pixels.show();
}


void rainbowCycle(uint8_t wait) {
  uint16_t i, j;

  for(j=0; j<256; j++) {
    for(i=0; i< pixels.numPixels(); i++) {
      pixels.setPixelColor(i, Wheel(((i * 256 / pixels.numPixels()) + j) & 255));
    }
    pixels.show();
    delay(wait);
  }
}

uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return pixels.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return pixels.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return pixels.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

void rainbowFade2White(int wait, int rainbowLoops, int whiteLoops) {
  int fadeVal=0, fadeMax=100;
  for(uint32_t firstPixelHue = 0; firstPixelHue < rainbowLoops*65536;
    firstPixelHue += 256) {
    for(int i=0; i<pixels.numPixels(); i++) {
      uint32_t pixelHue = firstPixelHue + (i * 65536L / pixels.numPixels());
      pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(pixelHue, 255,
        255 * fadeVal / fadeMax)));
    }

    pixels.show();
    delay(wait);

    if(firstPixelHue < 65536) {                              // First loop,
      if(fadeVal < fadeMax) fadeVal++;                       // fade in
    } else if(firstPixelHue >= ((rainbowLoops-1) * 65536)) { // Last loop,
      if(fadeVal > 0) fadeVal--;                             // fade out
    } else {
      fadeVal = fadeMax; // Interim loop, make sure fade is at max
    }
  }

  for(int k=0; k<whiteLoops; k++) {
    for(int j=0; j<256; j++) { // Ramp up 0 to 255
      // Fill entire pixels with white at gamma-corrected brightness level 'j':
      pixels.fill(pixels.Color(0, 0, 0, pixels.gamma8(j)));
      pixels.show();
    }
    delay(1000); // Pause 1 second
    for(int j=255; j>=0; j--) { // Ramp down 255 to 0
      pixels.fill(pixels.Color(0, 0, 0, pixels.gamma8(j)));
      pixels.show();
    }
  }

  delay(500); // Pause 1/2 second
}





// -------------------- ACCELEROMETRE --------------------
int x_moyenne = 0;

void calibrate(uint32_t timeout) {
    uint32_t timeStart = 0;
  
    int x_values = 0;
    int nb_x_values = 0;
  
    timeStart = millis();
    // Fill along the length of the pixels in various colors...
    
    rainbowFade2White(3, 10, 1);
  
    while ((millis() - timeStart) < timeout) {
        Serial.print(".");
  
        if (mode == 0) {
            // Rainbow mode
            uint16_t i, j;
            for(j=0; j<256; j++) {
                for(i=0; i< pixels.numPixels(); i++) {
                    pixels.setPixelColor(i, Wheel(((i * 256 / pixels.numPixels()) + j) & 255));
                }
                pixels.show();
                delay(2);
                
                x = icm20600.getAccelerationX();
                x_values += x;
                nb_x_values += 1;
            }
        }
    }
    x_moyenne = x_values / nb_x_values;
}


void get_acceleration() {
  int acc_x = icm20600.getAccelerationX() - x_moyenne;
  if (acc_x < -300) { 
    last_dcc_iter = 0;
  }
}


// -------------------- BLUETOOTH --------------------
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


void connect() {
      client_connected = true;
      Serial.println("Client bluetooth connecté !");
}

void disconnect() {
      client_connected = false;
      left = false;
      right = false;
      Serial.println("Client bluetooth déconnecté !");
}


String last_recieve = "";

String bluetooth_recv () {
  String text = last_recieve;
  while (true) {
    if (blueToothSerial.available()>0) {
      char recu = blueToothSerial.read();
      if (recu == '#') {
        break;
      } else {
        text = text + recu;
      }
    } else {
      last_recieve = text;
      return "";
    }
  }
  last_recieve = "";
  return text;
}

// -------------------- OTHER --------------------

bool test (String text, String contain) {
  return text == contain or text.indexOf(contain) != -1;
}
