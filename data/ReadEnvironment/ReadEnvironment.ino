/*
Read temperature and humidity from digital pin 10
Transmit over serial

The delays are used to control for noise on the serial line.
*/
#include "DHT.h"

#define tempSelection '5'
#define humiditySelection '6'

#define DHTPIN 10
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const int sensorPin = 10;
int x = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
  if ((x = Serial.available()) > 0){
      int x = Serial.read();
      if (x == tempSelection){
        float t = dht.readTemperature();

        if(isnan(t)) {
          Serial.println("-1");
        } else {
          Serial.println(t);
        }
      }

      else if (x == humiditySelection){
        float h = dht.readHumidity();

        if(isnan(h)) {
          Serial.println("-1");
        } else {
          Serial.println(h);
        }
      }
    }
}
