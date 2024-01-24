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
    byte recu;
    while(1){
        if(blueToothSerial.available()>0){
           while(blueToothSerial.available()) {
            byte recu = blueToothSerial.read();
            char charRecu = static_cast<char>(recu);
            if (charRecu == '#') {
              Serial.println();
            } else {
               Serial.print(charRecu);
            }
          }
       }   
    }
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
