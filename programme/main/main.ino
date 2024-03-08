// ================================================
//                      INIT
// ================================================

// -------------------- LED --------------------

#include "Adafruit_NeoPixel.h"
#ifdef __AVR__
#include <avr/power.h>
#endif
#define PIN 5
#define NUMPIXELS 16

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
uint32_t firstPixelHue = 0;
int firstPixel = 0;
int maxOpacity = 255;
int Brightness = 20;
int opacities[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

// -------------------- ACCELEROMETRE --------------------

#include "ICM20600.h"
#include <Wire.h>

ICM20600 icm20600(true);
int x_moyenne = 0;
int x;

// -------------------- BLUETOOTH --------------------

#include <SoftwareSerial.h> //Software Serial Port
#define RxD 10
#define TxD 11

SoftwareSerial blueToothSerial(RxD, TxD);
String last_recieve = "";
bool client_connected = false;
unsigned long lastCommunicationTime = 0;
const unsigned long timeoutDuration = 4000;

// -------------------- CAPTEUR ULTRA-SONS --------------------

#include "Ultrasonic.h"
Ultrasonic ultrasonic(7);
const int dist_secure = 300;
int last_dist = 0;

// -------------------- MOTOR --------------------

#include "Grove_Motor_Driver_TB6612FNG.h"

MotorDriver motor;

// set speed to 120 revolutions per minute
uint16_t rpm = 120;
const int pos_right = 20*50;
const int pos_left = -20*50;
const int pos_null = 0;
int go_pos = 0;
int pos = 0;

// -------------------- OTHER --------------------

bool left = false;
bool right = false;
bool warning = false;
bool dcc = false;
int led_mode = 1;
//  led_mode :
//     0 -> Rainbow
//     1 -> Blue

int loop_iter = 0;
int last_dcc_iter = -1;
int iter_led = 0;
int led_test = -1;


// ================================================
//                     SETUP
// ================================================

void setup()
{
    Serial.begin(9600);
    Serial.println("Démarrage en cours");

    // -------------------- LED --------------------
    
    // Led exemple :
    // https://wiki.seeedstudio.com/Grove-LED_ring/
    #if defined(__AVR_ATtiny85__)
        if (F_CPU == 16000000)
        {
            clock_prescale_set(clock_div_1);
        }
    #endif

    pixels.setBrightness(Brightness);
    pixels.begin();
    led_init();

    // -------------------- ACCELEROMETRE --------------------

    Wire.begin();
    icm20600.initialize();
    Serial.println("Start figure-8 calibration");
    calibrate(5000);
    Serial.println("Calibration ternimé");

    // -------------------- BLUETOOTH --------------------

    pinMode(RxD, INPUT);
    pinMode(TxD, OUTPUT);
    setupBlueToothConnection();

    // -------------------- MOTOR --------------------
    
    motor.init();
    
    // -------------------- INIT FINISH --------------------
    
    led_pulse(35000);
    
    Serial.println("Démarrage en terminé");
}

// ================================================
//                   MAIN LOOP
// ================================================

void loop()
{
    loop_iter = loop_iter + 1;

    // Update last dcc iter loop
    if (last_dcc_iter >= 0)
    {
        last_dcc_iter += 1;
    }
    // Reset last dcc iter loop
    if (last_dcc_iter >= 30)
    {
        last_dcc_iter = -1;
    }

    // Détecter la déconnection
    if (millis() - lastCommunicationTime > timeoutDuration and client_connected)
    {
        Serial.println("BlueTooth TimeOut");
        b_disconnect();
    }

    // Détecter la réception
    String recept = bluetooth_recv();
    if (recept != "")
    {
        // Update lastCommunicationTime
        if (lastCommunicationTime < millis())
        {
            lastCommunicationTime = millis();
        }
        
        Serial.println(recept);

        if (test(recept, "co"))
        {
            Serial.println("App Signal");
            b_connect();
        }
        else if (test(recept, "de") and client_connected)
        {
            Serial.println("App Signal");
            b_disconnect();
        }
        else if (test(recept, "s_r") and client_connected)
        {
            right = false;
            go_pos = pos_null;
        }
        else if (test(recept, "r") and client_connected)
        {
            left = false;
            right = true;
            go_pos = pos_right;
            iter_led = 0;
        }
        else if (test(recept, "s_l") and client_connected)
        {
            left = false;
            go_pos = pos_null;
        }
        else if (test(recept, "l") and client_connected)
        {
            right = false;
            left = true;
            go_pos = pos_left;
            iter_led = 0;
        }
        else if (test(recept, "s_w") and client_connected)
        {
            warning = false;
        }
        else if (test(recept, "w") and client_connected)
        {
            warning = true;
            iter_led = 0;
        }
        else if (test(recept, "s_stop") and client_connected)
        {
            dcc = false;
        }
        else if (test(recept, "stop") and client_connected)
        {
            dcc = true;
        }
        else if (test(recept, "m:") and client_connected)
        {
            if (test(recept, "d"))
            {
                pos_right += 20;
                pos_left += 20;
                pos_null += 20;
                go_pos += 20;
            }
            else if (test(recept, "g"))
            {
                pos_right -= 20;
                pos_left -= 20;
                pos_null -= 20;
                go_pos -= 20;
            }
        }
        else if (test(recept, "b:") and client_connected)
        {
            int positionDeuxPoints = recept.indexOf(':');
            String valeurString = recept.substring(positionDeuxPoints + 1);
            int valeurInt = valeurString.toInt();
            Brightness = valeurInt;
            pixels.setBrightness(valeurInt);
        }
        else if (test(recept, "c:") and client_connected)
        {
            if (test(recept, "d"))
            {
                led_mode = 1;
                led_test = 0;
            }
            else if (test(recept, "y"))
            {
                led_mode = 2;
                led_test = 0;
            }
            else if (test(recept, "g"))
            {
                led_mode = 3;
                led_test = 0;
            }
            else if (test(recept, "b"))
            {
                led_mode = 4;
                led_test = 0;
            }
            else if (test(recept, "v"))
            {
                led_mode = 5;
                led_test = 0;
            }
            else if (test(recept, "m"))
            {
                led_mode = 0;
                led_test = 0;
            }
        }
        else if (not client_connected) {
            Serial.println("Recieve Signal");
            b_connect();
        }
    }

    // Détecter l'entrée
    if (Serial.available() > 0)
    {
        String text = Serial.readString();
        blueToothSerial.print("p:");
        blueToothSerial.print(text);
        blueToothSerial.print('#');
    }

    // Moteur
    if (go_pos > pos) 
    {
      droite();
    }
    if (go_pos < pos) 
    {
      gauche();
    }
    
    // Envoyer des messages
    if (loop_iter >= 50)
    {
        if (client_connected)
        {
            // Laisser une variable à envoyer régulièrement pour ping le client
            blueToothSerial.print("b:");
            blueToothSerial.print(Brightness);
            blueToothSerial.print('#');
            
            last_dist = ultrasonic.MeasureInCentimeters();
            blueToothSerial.print("d:");
            blueToothSerial.print(last_dist);
            blueToothSerial.print('#');
        }

        loop_iter = 0;
    }

    get_acceleration();

    if (iter_led >= 80)
    {
        iter_led = 0;
    }
    
    led();
    
    delay(10);
}

// ================================================
//                 OTHER FUNCTIONS
// ================================================

// -------------------- LED --------------------

void led()
{
    iter_led = iter_led + 1;
    // Update led_test iter loop
    if (led_test >= 0)
    {
        led_test += 1;
    }
    // Reset led_test iter loop
    if (led_test >= 100)
    {
        led_test = -1;
    }

    // Reset all Led
    led_clean();

    if ((last_dcc_iter >= 0 and client_connected) or dcc) // Décélération
    {
        switch(led_mode)
        {
            case 0:
                led_rainbow(0, 16);
                break;
            case 1:
                led_show(0, 16, 255, 0, 0, 255); // Red
                break;
            case 2:
                led_show(0, 16, 255, 40, 0, 255); // Orange
                break;
            case 3:
                led_show(0, 16, 0, 255, 0, 255); // Green
                break;
            case 4:
                led_show(0, 16, 0, 0, 255, 255); // Blue
                break;
            case 5:
                led_show(0, 16, 200, 0, 255, 255); // Purple
                break;
        }
    }
    if (right or warning or 0 < last_dist < dist_secure)
    {
        if (iter_led <= 40)
        {   
            switch(led_mode)
            {
                case 0:
                    led_rainbow(9, 14);
                    break;
                case 1:
                    led_show(9, 14, 255, 40, 0, 255); // Orange
                    break;
                case 2:
                    led_show(9, 14, 255, 200, 0, 255); // Yellow
                    break;
                case 3:
                    led_show(9, 14, 100, 255, 0, 255); // Yellow/Green
                    break;
                case 4:
                    led_show(9, 14, 0, 200, 255, 255); // Cyan
                    break;
                case 5:
                    led_show(9, 14, 40, 0, 255, 255); // Blue
                    break;
            }
        }
        else
        {
            led_show(9, 14, 0, 0, 0, 0);
        }
    }
    if (left or warning or 0 < last_dist < dist_secure)
    {
        if (iter_led <= 40)
        {
            switch(led_mode)
            {
                case 0:
                    led_rainbow(1, 6);
                    break;
                case 1:
                    led_show(1, 6, 255, 40, 0, 255); // Orange
                    break;
                case 2:
                    led_show(1, 6, 255, 200, 0, 255); // Yellow
                    break;
                case 3:
                    led_show(1, 6, 100, 255, 0, 255); // Yellow/Green
                    break;
                case 4:
                    led_show(1, 6, 0, 200, 255, 255); // Cyan
                    break;
                case 5:
                    led_show(1, 6, 40, 0, 255, 255); // Blue
                    break;
            }
        }
        else
        {
            led_show(1, 6, 0, 0, 0, 0);
        }
    }
    if (led_test >= 0)
    {
        led_clean();
        switch(led_mode)
            {
                case 0:
                    led_rainbow(0, 16);
                    break;
                case 1:
                    led_pattern(255, 40, 0, 255, 0, 0); // Orange
                    break;
                case 2:
                    led_pattern(255, 200, 0, 255, 40, 0); // Yellow
                    break;
                case 3:
                    led_pattern(100, 255, 0, 0, 255, 0); // Yellow/Green
                    break;
                case 4:
                    led_pattern(0, 200, 255, 0, 0, 255); // Cyan
                    break;
                case 5:
                    led_pattern(40, 0, 255, 200, 0, 255); // Blue
                    break;
            }
    }

    pixels.show();

    // Update rainbow cycle
    if (firstPixelHue > 65536)
        firstPixelHue = 0;
    firstPixelHue += 256;
}

void led_clean()
{
    pixels.clear();
}

void led_show(int led_start, int led_finish, int r, int g, int b, int a)
{
    for (int i = led_start; i < led_finish; i++)
    {
        pixels.setPixelColor(i, pixels.Color(r, g, b, a));
    }
}

void led_rainbow(int led_start, int led_finish)
{
    for (int i = led_start; i < led_finish; i++)
    {
        uint32_t pixelHue = firstPixelHue + (i * 65536L / pixels.numPixels());
        pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(pixelHue, 255, 255)));
    }
}

void led_pulse(int color)
{
    float a = 0;
    while (a <= 3.14)
    {
        for (int i = 0; i < 16; i++)
        {
            pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(color, 255, 255 * sin(a))));
        }

        pixels.show();
        a += 0.01;
        if (1.56 <= a and a <= 1.58 )
        {
            delay(500);
            a = 1.59;
        }
        delay(3);
    }
}

void led_init()
{
    int temp = 0;
    while (temp < 1000)
    {
        led_clean();
        for (int i = 0; i < 16; i++)
        {
            pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(0, 255, 0)));
        }
        temp += 1;
    }
}

void led_pattern(int r, int g, int b, int r_, int g_, int b_)
{   
    int led_num = 2;
    for (int i = 0; i < 16; i++)
    {
        if (led_num < 3)
        {
            pixels.setPixelColor(i, pixels.Color(r_, g_, b_, 255));
        }
        else
        {
            pixels.setPixelColor(i, pixels.Color(r, g, b, 255));
        }
        if (led_num > 6)
        {
          led_num = -1;
        }
    led_num += 1;
    }
}


// -------------------- ACCELEROMETRE --------------------

void calibrate(uint32_t timeout)
{
    uint32_t timeStart = 0;

    int x_values = 0;
    int nb_x_values = 0;

    timeStart = millis();

    while ((millis() - timeStart) < timeout)
    {
        if (led_mode == 0)
        {
            int nb_loop = 10;
            int fadeVal = 0, fadeMax = 100;
            for (uint32_t firstPixelHue = 0; firstPixelHue < nb_loop * 65536; firstPixelHue += 256)
            {
                for (int i = 0; i < pixels.numPixels(); i++)
                {
                    uint32_t pixelHue = firstPixelHue + (i * 65536L / pixels.numPixels());
                    pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(pixelHue, 255, 255 * fadeVal / fadeMax)));
                }
                pixels.show();
                delay(3);
                // Stop loop
                if ((millis() - timeStart) > timeout)
                    nb_loop = firstPixelHue / 65536 + 1;
                if (firstPixelHue < 65536)
                { // First loop,
                    if (fadeVal < fadeMax)
                        fadeVal++; // fade in
                }
                else if (firstPixelHue >= ((nb_loop - 1) * 65536))
                { // Last loop,
                    if (fadeVal > 0)
                        fadeVal--; // fade out
                }
                else
                {
                    fadeVal = fadeMax; // Interim loop, make sure fade is at max
                }
                x_values += x;
                nb_x_values += 1;
            }
        }
        else
        {
            for (int i = 0; i < 16; i++)
            {
                opacities[i] -= 20;
                if (opacities[i] < 0) opacities[i] = 0;
                int opacity = opacities[i];
                /* Color code :
                 *  - Dark blue : 40000
                 *  - Cyan : 35000
                 *  - Red : 0
                 *  - Green : 20500
                 */
                pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(35000, 255, opacity)));
            }

            pixels.show();
            opacities[firstPixel] = maxOpacity;
            firstPixel += 1;
            if (firstPixel >= 16) firstPixel = 0;
            if ((millis() - timeStart) > timeout - 1100) maxOpacity -= 10;
            delay(50);
            x_values += x;
            nb_x_values += 1;
        }
    }
    x_moyenne = x_values / nb_x_values;
}

void get_acceleration()
{
    int acc_x = icm20600.getAccelerationX() - x_moyenne;
    if (acc_x < -350)
    {
        last_dcc_iter = 0;
    }
}

// -------------------- BLUETOOTH --------------------

void setupBlueToothConnection()
{
    blueToothSerial.begin(9600);
    blueToothSerial.print("AT");
    delay(400);
    blueToothSerial.print("AT+DEFAULT"); // Restore all setup value to factory setup
    delay(400);
    blueToothSerial.print("AT+NAMESafe_Cycling"); // set the bluetooth name as "Safe_Cycling"
    delay(400);
    blueToothSerial.print("AT+PIN1234"); // set the pair code to connect
    delay(400);
    blueToothSerial.print("AT+AUTH1");
    delay(400);
    blueToothSerial.flush();
}

void b_connect()
{
    blueToothSerial.print("ok");
    led_pulse(25000);
    client_connected = true;
    reset_led();
    Serial.println("Client bluetooth connecté !");
    lastCommunicationTime = millis();
}

void b_disconnect()
{
    led_pulse(100);
    client_connected = false;
    go_pos = pos_null;
    reset_led();
    Serial.println("Client bluetooth déconnecté !");
}

void reset_led()
{
    left = false;
    right = false;
    warning = false;
    dcc = false;
    last_dist = 0;
}

String bluetooth_recv()
{
    String text = last_recieve;
    while (true)
    {
        if (blueToothSerial.available() > 0)
        {
            char recu = blueToothSerial.read();
            if (recu == '#')
            {
                break;
            }
            else
            {
                text = text + recu;
            }
        }
        else
        {
            last_recieve = text;
            return "";
        }
    }
    last_recieve = "";
    return text;
}

// -------------------- MOTOR --------------------

void droite(){
  int s = 20;
  motor.stepperRun(HALF_STEP, s, rpm);
  pos += s;
}

void gauche(){
  int s = -20;
  motor.stepperRun(HALF_STEP, s, rpm);
  pos += s;
}

// -------------------- OTHER --------------------

bool test(String text, String contain)
{
    return text == contain or text.indexOf(contain) != -1;
}
