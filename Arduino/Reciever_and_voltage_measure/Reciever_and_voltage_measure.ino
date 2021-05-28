#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>


//Radio Vars
RF24 radio(9, 10); // CE, CSN
const byte address[6] = "10001";
boolean button_state = 0;
int led_pin = 3;

//Voltage Vars
float val = 0;
int analogPin = 19;
float divi = 0.6;
int nRun = 0;

void setup() {
  pinMode(6, OUTPUT);
  pinMode(analogPin, INPUT);
  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);   //Setting the address at which we will receive the data
  radio.setPALevel(RF24_PA_MIN);       //You can set this as minimum or maximum depending on the distance between the transmitter and receiver.
  radio.startListening();              //This sets the module as receiver
}

void loop()
{
  if (radio.available())              //Looking for the data.
  {
    char text[32] = "";                 //Saving the incoming data
    radio.read(&text, sizeof(text));    //Reading the data
    Serial.println(text);
  }

  if(nRun >= 60){
    val = analogRead(analogPin);    // read the input pin
    val = mapf(val, 0, 1023, 0, 14.3);
    Serial.println("V:"+String(val));
    nRun = 0;
  }

  nRun++;
  delay(5);
}

//Map for floats
float mapf(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
