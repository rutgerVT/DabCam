#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

//--------EDIT THESE---------
int conNr = 1;  //Make sure one of your dabcons is 1 and the other is 2!
RF24 radio(9, 10); // CE, CSN         
const byte address[6] = "10001";     //Byte of array representing the address. This is the address where we will send the data. This should be same on the receiving side.



int button_pin = 2;
boolean button_state = 0;
float lastMag = 0;

void setup() {
  pinMode(button_pin, INPUT);
  radio.begin();                  //Starting the Wireless communication
  radio.openWritingPipe(address); //Setting the address where we will send the data
  radio.setPALevel(RF24_PA_HIGH);  //You can set it as minimum or maximum depending on the distance between the transmitter and receiver.
  radio.stopListening();          //This sets the module as transmitter

  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_16G))
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    delay(500);
  }

  mpu.setAccelPowerOnDelay(MPU6050_DELAY_3MS);

  mpu.setIntFreeFallEnabled(false);  
  mpu.setIntZeroMotionEnabled(false);
  mpu.setIntMotionEnabled(false);
  
  mpu.setDHPFMode(MPU6050_DHPF_5HZ);

  mpu.setMotionDetectionThreshold(2);
  mpu.setMotionDetectionDuration(5);

  mpu.setZeroMotionDetectionThreshold(4);
  mpu.setZeroMotionDetectionDuration(2);  
  
  //checkSettings();

  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);

  pinMode(7, OUTPUT);
  digitalWrite(7, LOW);  
}


void loop()
{
  Vector rawAccel = mpu.readRawAccel();
  
  float accX = ((float)rawAccel.XAxis) / 16384.0;
  float accY = ((float)rawAccel.YAxis) / 16384.0;
  float accZ = ((float)rawAccel.ZAxis) / 16384.0;

  float magnitude = abs(accX) + abs(accY) + abs(accZ);

  //String txt = "1: "+String((magnitude - lastMag)*100);
  String txt = String(conNr)+": "+ String(magnitude*100);

  //if(magnitude - lastMag < -0.1 || magnitude-lastMag > 0.1){
    radio.write(txt.c_str(), txt.length());
  //}

  //lastMag = magnitude;
  delay(33);
}
