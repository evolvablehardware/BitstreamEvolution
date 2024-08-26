#define STATE_PIN 4
#define OSC_PIN   3
#define SYNCH_PIN 2

#define NUM_INTERVALS     10
#define LOW_FREQ          40
#define HIGH_FREQ         200
#define TONE_LEN          250

int stateOrder[NUM_INTERVALS] = {0, 1, 0, 1, 0, 1, 0, 1, 0, 1};

int generating = 0;
int state;

void setup()
{
  pinMode(OSC_PIN, OUTPUT);
  pinMode(STATE_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SYNCH_PIN, INPUT);

  digitalWrite(LED_BUILTIN, 0);
  digitalWrite(STATE_PIN, 0);
  digitalWrite(OSC_PIN, 0);
  attachInterrupt(digitalPinToInterrupt(SYNCH_PIN), startGenerate, RISING);

/*
  shuffleStates();
  while (countToggles() <= 3)
  {
    shuffleStates();
  }
*/
}

void loop()
{
  if (generating)
  {
    for (int i = 0; i < NUM_INTERVALS; i++)
    {
      state = stateOrder[i];
      digitalWrite(LED_BUILTIN, state);
      digitalWrite(STATE_PIN, state);
      if (!state)
      {
        tone(OSC_PIN, LOW_FREQ, TONE_LEN);
        delay(TONE_LEN);
      }
      else
      {
        tone(OSC_PIN, HIGH_FREQ, TONE_LEN);
        delay(TONE_LEN);
      }
    }
    generating = 0;
    /*
    shuffleStates();
    while (countToggles() <= 3)
    {
      shuffleStates();
    }
    */
    digitalWrite(STATE_PIN, 0);
    digitalWrite(OSC_PIN, 0);
    digitalWrite(LED_BUILTIN, 0);
    delay(10);
  }
}

void startGenerate()
{
  generating = 1;
}

void shuffleStates()
{
  int temp;
  int n;
  int i;
  for (i = 0; i < NUM_INTERVALS; i++)
  {
    n = random(0, NUM_INTERVALS);
    temp = stateOrder[n];
    stateOrder[n] =  stateOrder[i];
    stateOrder[i] = temp;
  }
  for (i = 0; i < NUM_INTERVALS; i++)
  {
    Serial.print(stateOrder[i]);
  }
  Serial.println("");
}

int countToggles()
{
  int count;
  for (int i = 0; i < NUM_INTERVALS - 1; i++)
  {
    if (stateOrder[i] != stateOrder[i + 1])
    {
      count++;
    }
  }
  return count;
}
