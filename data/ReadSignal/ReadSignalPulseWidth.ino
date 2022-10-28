/* -------------------------------------------------------------------------- */
/*                                 Pulse Width                                */
/* -------------------------------------------------------------------------- */

const int analogPin = A0;
const int interrupt = 2;
bool led_thingy = false;

int buf[500]; //500 integers at 10 uS intervals = 5 mS
volatile long pulseCount = 0;
unsigned long pulseLength = 0;
int sampleNumber = 5;
int x = 0;


/* ---------------------------------- Setup --------------------------------- */
void setup(){
    //analogReference(EXTERNAL);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(interrupt, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    Serial.begin(115200);
    Serial.println("Began serial");
    while (!Serial);
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(2, HIGH); // noise suppression on interrupt pin
    attachInterrupt(digitalPinToInterrupt(interrupt),pulseCounter, RISING); // can be changed from RISING to FALLING or CHANGE
}

void pulseCounter(){
    pulseCount++;
}


/* ---------------------------------- Loop ---------------------------------- */
void loop(){
    if ((x = Serial.available()) > 0){
      int x = Serial.read();
      
      if (x == '2'){
        Serial.print("START\nSTART\nSTART\n");

//        for(int t=0; t<=499; t++){
//          buf[t] = analogRead(analogPin); //Read the AnalogPin
//          delayMicroseconds(10); //Wait 10 uS
//        }

        for(int i=0; i<=499; i++){
            Serial.print(i+1);
            Serial.print(": ");
            // Send back the buffer array
            //Serial.println(buf[i]);
            Serial.print(analogRead(analogPin)); //buf[i]); //Write the buffer to Serial
            Serial.print("\n");
            // This determines the sampling frequency 
            //(500 samples delayed by 10us each results in a sampled time interval of 5ms)
            delayMicroseconds(10); 
        }
    
        Serial.print("FINISHED\nFINISHED\nFINISHED\n");
        delay(10); //3016/1508 Delay to load the FPGA
      }
      else if (x == '1'){

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

      }
    }
}
