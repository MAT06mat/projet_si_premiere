#include <SoftwareSerial.h>   //Software Serial Port
#define RxD         10
#define TxD         11
#define PINLED      9

SoftwareSerial blueToothSerial(RxD,TxD);

void setup(){
    Serial.begin(9600);
    Serial.println("Démarrage en cours");
    pinMode(RxD, INPUT);
    pinMode(TxD, OUTPUT);
    pinMode(PINLED, OUTPUT);
    setupBlueToothConnection();
    Serial.println("Démarrage ternimé");
}

void loop(){
   String recept = bluetooth_recv();
   if (recept != "") {
    Serial.println(recept);
   }
   if (Serial.available() > 0) {
    String text = Serial.readString();
    bluetooth_send(text);
   }
  bspeed(speed);
  speed = speed + 1;
  delay(100);
}

String bluetooth_recv () {
  byte recu;
  String text = "";
  if(blueToothSerial.available()>0){
     while(blueToothSerial.available()) {
        byte recu = blueToothSerial.read();
        char charRecu = static_cast<char>(recu);
        if (charRecu == '#') {
          return text;
        } else {
           text = text + charRecu;
        }
     }
  }
  return text;
}


void bspeed(const String& text) {
  blueToothSerial.print("set-speed-");
  blueToothSerial.print(text);
  blueToothSerial.print('#');
}


void bluetooth_send(const String& text) {
  blueToothSerial.print("print-");
  blueToothSerial.print(text);
  blueToothSerial.print('#');
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
