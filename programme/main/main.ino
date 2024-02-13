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
int opacities[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

// -------------------- ACCELEROMETRE --------------------

#include "ICM20600.h"
#include <Wire.h>

ICM20600 icm20600(true);
int x_moyenne = 0;
int x;

// -------------------- BLUETOOTH --------------------

#include <SoftwareSerial.h> //Software Serial Port
#define RxD 6
#define TxD 7

SoftwareSerial blueToothSerial(RxD, TxD);
String last_recieve = "";
bool client_connected = false;
unsigned long lastCommunicationTime = 0;
const unsigned long timeoutDuration = 3000;

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

    pixels.setBrightness(10);
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

        if (test(recept, "c"))
        {
            Serial.println("App Signal");
            b_connect();
        }
        else if (test(recept, "d") and client_connected)
        {
            Serial.println("App Signal");
            b_disconnect();
        }
        else if (test(recept, "s_r") and client_connected)
        {
            right = false;
        }
        else if (test(recept, "r") and client_connected)
        {
            left = false;
            right = true;
            iter_led = 0;
        }
        else if (test(recept, "s_l") and client_connected)
        {
            left = false;
        }
        else if (test(recept, "l") and client_connected)
        {
            right = false;
            left = true;
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
        } else if (not client_connected) {
            Serial.println("Recieve Signal");
            b_connect();
        }
    }

    // Détecter l'entrée
    if (Serial.available() > 0)
    {
        String text = Serial.readString();
        blueToothSerial.print("print:");
        blueToothSerial.print(text);
        blueToothSerial.print('#');
    }

    // Envoyer des messages
    if (loop_iter >= 100)
    {
        loop_iter = 0;
        // Laisser une variable à envoyer régulièrement pour ping le client
        blueToothSerial.print("speed:");
        blueToothSerial.print(last_dcc_iter);
        blueToothSerial.print('#');
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

    // Reset all Led
    led_clean();

    if ((last_dcc_iter >= 0 and client_connected) or dcc)
    {
        if (led_mode == 0)
        {
            led_rainbow(0, 16);
        }
        else
        {
            // Set all Led to red
            led_show(0, 16, 255, 0, 0);
        }
    }
    if (right or warning)
    {
        if (iter_led <= 40)
        {
            if (led_mode == 0)
            {
                led_rainbow(9, 14);
            }
            else
            {
                // Set right Led to orange
                led_show(9, 14, 255, 40, 0);
            }
        }
    }
    if (left or warning)
    {
        if (iter_led <= 40)
        {
            if (led_mode == 0)
            {
                led_rainbow(1, 6);
            }
            else
            {
                // Set left Led to orange
                led_show(1, 6, 255, 40, 0);
            }
        }
    }

    // Update rainbow cycle
    if (firstPixelHue > 65536)
        firstPixelHue = 0;
    firstPixelHue += 256;
}

void led_clean()
{
    pixels.clear();
    pixels.show();
}

void led_show(int led_start, int led_finish, int r, int g, int b)
{
    for (int i = led_start; i < led_finish; i++)
    {
        pixels.setPixelColor(i, pixels.Color(r, g, b, 255));
    }
    pixels.show();
}

void led_rainbow(int led_start, int led_finish)
{
    for (int i = led_start; i < led_finish; i++)
    {
        uint32_t pixelHue = firstPixelHue + (i * 65536L / pixels.numPixels());
        pixels.setPixelColor(i, pixels.gamma32(pixels.ColorHSV(pixelHue, 255, 255)));
    }
    pixels.show();
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
                 *  - Green : 25500
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
    if (acc_x < -300)
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
    led_pulse(25500);
    client_connected = true;
    reset_led();
    Serial.println("Client bluetooth connecté !");
    lastCommunicationTime = millis();
}

void b_disconnect()
{
    led_pulse(100);
    client_connected = false;
    reset_led();
    Serial.println("Client bluetooth déconnecté !");
}

void reset_led()
{
    left = false;
    right = false;
    warning = false;
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

// -------------------- OTHER --------------------

bool test(String text, String contain)
{
    return text == contain or text.indexOf(contain) != -1;
}
