/*
Read analog voltage value from analog IN (pin 2)
Convert it to digital value and transmit over serial

The delays are used to control for noise on the serial line.
*/

#define pulseWidthMeasureSelection '3'
#define pulseCountMeasureSelection '1'
#define ADCMeasureSelection '2' 
#define switchConstant '4'
#define ADCMeasuretdSelection '5'

int analogPin = A0;
int digitalPin = 3;
int interrupt = 2;
int synchPin = 4;
bool led_thingy = false;

int buf[500]; //500 integers at 10 uS intervals = 5 mS
volatile long pulseCount = 0;
unsigned long pulseLength = 0;
int sampleNumber = 5;
int x = 0;

/* ---------------------------------- Setup --------------------------------- */
void setup(){
    
    /*  Set analog reference point, 
        external uses the voltage applied to the AREF pin
    */
    //analogReference(EXTERNAL);
    
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(synchPin, OUTPUT);
    pinMode(interrupt, INPUT);
    pinMode(analogPin, INPUT);
    pinMode(digitalPin, INPUT);

    digitalWrite(LED_BUILTIN, LOW);
    Serial.begin(115200);
    Serial.println("Began serial");
    while (!Serial);
    digitalWrite(LED_BUILTIN, HIGH);

    // noise suppression on interrupt pin
    //commented out because it was messing with reading of a0
    // digitalWrite(2, HIGH); 

    // can be changed from RISING to FALLING or CHANGE
    attachInterrupt(digitalPinToInterrupt(interrupt),pulseCounter, RISING); 
}


// This method is attached to the interrupt to count pulses
void pulseCounter(){
    pulseCount++;
}

/* ---------------------------------- Loop ---------------------------------- */
void loop(){
    if ((x = Serial.available()) > 0){
      int x = Serial.read();
      
      if (x == ADCMeasureSelection){
        Serial.print("START\nSTART\nSTART\n");

        for(int i=0; i<=499; i++){
            Serial.print(i+1);
            Serial.print(": ");
            Serial.print(analogRead(analogPin)); //buf[i]); //Write the buffer to Serial
            Serial.print("\n");
            // This determines the sampling frequency 
            //(500 samples delayed by 10us each results in a sampled time interval of 5ms)
            delayMicroseconds(10); 
        }
    
        Serial.print("FINISHED\nFINISHED\nFINISHED\n");
        delay(10); //3016/1508 Delay to load the FPGA
      }
      else if (x == ADCMeasuretdSelection){
        Serial.print("START\nSTART\nSTART\n");
        digitalWrite(synchPin, HIGH);
        digitalWrite(LED_BUILTIN, LOW);

        for(int i=0; i<=999; i++){
            Serial.print(i+1);
            Serial.print(": ");
            Serial.print(analogRead(analogPin)); //buf[i]); //Write the buffer to Serial
            Serial.print(" ");
            Serial.print(digitalRead(digitalPin)); //buf[i]); //Write the buffer to Serial
            Serial.print("\n");
            // This determines the sampling frequency 
            //(500 samples delayed by 2 ms each results in a sampled time interval of 1 second)
            delayMicroseconds(1950); 
        }

        digitalWrite(synchPin, LOW);
        digitalWrite(LED_BUILTIN, HIGH);
    
        Serial.print("FINISHED\nFINISHED\nFINISHED\n");
        delay(1000);
        x = 0;
        // delay(10); //3016/1508 Delay to load the FPGA
      }
      else if (x == pulseCountMeasureSelection){
        //Serial.print("START\nSTART\nSTART\n"); // currently breaks measure_pulses()
        //PULSE COUNT   //using interrupt
        cli(); //disable interrupt pin
        pulseCount = 0;
        sei(); //enable interrupt pin

        // Check to see if this is actually one second
        delay(1000);
        Serial.println(pulseCount);
        // Serial.print("FINISHED\nFINISHED\nFINISHED\n");  // currently breaks measure_pulses()
        delay(10); //3016/1508 Delay to load the FPGA
      }

      else if(x == pulseWidthMeasureSelection)
      {
        Serial.print("START\nSTART\nSTART\n");
       //pulse width measurement
       int timeTracker = 0;
       int result = 0;
       int i = 0;

       while (timeTracker <= 1050){ // 1.05ms
         long tempResult = pulseIn(analogPin, HIGH, 1050);
         if (tempResult >= 1000){
           result = tempResult;
           break;
         }
         timeTracker += tempResult;
         buf[i]= tempResult;
         i++;
       }

      Serial.print(result);
      Serial.print("FINISHED\nFINISHED\nFINISHED\n");
      delay(10); //3016/1508 Delay to load the FPGA
      
      }

      else if(x == switchConstant)
      {
        detachInterrupt(digitalPinToInterrupt(interrupt));
        if(analogPin == A0) {
          analogPin = A6;
          interrupt = 3;
        } else {
          analogPin = A0;
          interrupt = 2;
        }
        attachInterrupt(digitalPinToInterrupt(interrupt),pulseCounter, RISING);
      }
    }
}
