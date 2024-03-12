int statePin = 2;
int oscillatorPin = 3;
int is10K = 0;
int counter = 0;
int isHigh = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(oscillatorPin, OUTPUT);
  pinMode(statePin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(statePin, is10K);
  digitalWrite(oscillatorPin, isHigh);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(oscillatorPin, isHigh);
  counter++;
  if ((is10K == 0 && counter == 1000) || (is10K == 1 && counter == 10000))
  {
    is10K = 1 - is10K;
    digitalWrite(statePin, is10K);
    digitalWrite(LED_BUILTIN, is10K);
    counter = 0;
  }
  isHigh = 1 - isHigh;
  if (is10K == 0)
  {
    isHigh = 0;
    digitalWrite(oscillatorPin, LOW);
    counter = 0;
    delay(500);
    is10K = 1 - is10K;
    digitalWrite(statePin, is10K);
    digitalWrite(LED_BUILTIN, is10K);
    // delayMicroseconds(500);
  }
  else
  {
    delayMicroseconds(43);
  }
}
