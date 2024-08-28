// Pin D4 is used to transmit the state of the generated square wave.
// If State = 0 (LOW), then the square wave is at the lower frequency (e.g. 1 kHz)
// If State = 1 (HIGH), then the square wave is at the higher frequency (e.g. 10 kHz)

// Pin D3 is used to transmit the actual square wave to the FPGA.

// Pin D2 is used for synchronization with the data-collecting Nano.
// The data-collecting Nano pulls the synchronization signal high to tell
// this signal-generating Nano to begin the 2.5 second transmission of a square wave.

#define STATE_PIN 4
#define OSC_PIN   3
#define SYNCH_PIN 2

// Each 2.5 second interval has 10 frequency bursts. Five will be at a lower
// frequency, and five will be at a higher freqency.

// In Thompson's experiment, the low frequency was 1 kHz and the high frequency was 10 kHz.
// Right now, we are using 40 Hz and 200 Hz because our sampling rate of the data-collecting Nano
// is only 1000 samples in 2.5 seconds, or 400 Hz. 

// Each frequency burst's tone length is 250 ms so that 10 of them will take up the 2.5 second interval
#define NUM_INTERVALS     10
#define LOW_FREQ          40
#define HIGH_FREQ         200
#define TONE_LEN          250

// Initialize order of states to LOW, HIGH, LOW, HIGH, ...
int stateOrder[NUM_INTERVALS] = {0, 1, 0, 1, 0, 1, 0, 1, 0, 1};

// generating tracks whether or not the signal is being transmitted on pin D3.
int generating = 0;
int state;

void setup()
{
  // Configure pins
  pinMode(OSC_PIN, OUTPUT);
  pinMode(STATE_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SYNCH_PIN, INPUT);

  // Reset digital outputs
  digitalWrite(LED_BUILTIN, 0);
  digitalWrite(STATE_PIN, 0);
  digitalWrite(OSC_PIN, 0);

  // Configure pin D2 to detect rising edges from the data-collecting Nano
  // This way, the signal generation will begin as soon as the signal-generating Nano is prompted.
  attachInterrupt(digitalPinToInterrupt(SYNCH_PIN), startGenerate, RISING);

// NOTE: Thompson randomized the order of the frequency bursts every iteration.
// If you would like to do this, uncomment shuffleStates().
// If not, the states will be in the following order: 0 1 0 1 0 1 0 1 0 1
// If you would like to guarantee at least 3 low to high OR high to low transitions in the state,
// uncomment the while loop as well.

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
  // If signal is being generated, do the needful.
  if (generating)
  {
    // For 10 intervals, transmit the square wave of correct frequency.
    for (int i = 0; i < NUM_INTERVALS; i++)
    {
      // Read the next state to figure out whether to use a LOW or HIGH frequency wave
      state = stateOrder[i];

      // If State = 0, turn off LED. If State = 1, turn on LED
      digitalWrite(LED_BUILTIN, state);

      // Transmit the next state over the D4 pin.
      digitalWrite(STATE_PIN, state);

      // If State == 0, invoke tone() with the low frequency
      if (!state)
      {
        tone(OSC_PIN, LOW_FREQ, TONE_LEN);
        delay(TONE_LEN);
      }
      // If State == 1, invoke tone() with the high frequency
      else
      {
        tone(OSC_PIN, HIGH_FREQ, TONE_LEN);
        delay(TONE_LEN);
      }
    }
    // When done with the 2.5 second interval, reset generating
    generating = 0;

    // OPTIONAL: shuffle the order of states every time and ensure at least 3 transitions
    /*
    shuffleStates();
    while (countToggles() <= 3)
    {
      shuffleStates();
    }
    */

    // Reset outputs
    digitalWrite(STATE_PIN, 0);
    digitalWrite(OSC_PIN, 0);
    digitalWrite(LED_BUILTIN, 0);
    delay(10);
  }
}

// Interrupt handler. When synchronization pin is triggered, start signal generation.
void startGenerate()
{
  generating = 1;
}

// Shuffles the array of 10 states (five 0s, five 1s)
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

// Counts the number of low to high or high to low transitions
// Ex: 0101010101 --> 9 toggles
// Ex: 0000011111 --> 1 toggle
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
