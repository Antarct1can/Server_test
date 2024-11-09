volatile int speed = 0;
volatile int speedR = 0;
volatile int speedL = 0;
volatile int readingR = 0;
volatile int readingL = 0;
unsigned long timerR = 0;
unsigned long timerL = 0;
unsigned long prevtimerR = 0;
unsigned long prevtimerL = 0;
volatile unsigned long deltatimeR = 0;
volatile unsigned long deltatimeL = 0;
volatile float freqR = 0;
volatile float freqL = 0;

int pinR = 5;
int pinL = 6;
int pinreadingR = 2;
int pinreadingL = 3;

void setup() 
{
  Serial.begin(400000);
  pinMode(pinR,OUTPUT);
  pinMode(pinL,OUTPUT);
  pinMode(pinreadingR,INPUT);
  pinMode(pinreadingL,INPUT);
  attachInterrupt(digitalPinToInterrupt(pinreadingR), checkspeedR, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinreadingL), checkspeedL, FALLING);
}

void loop() 
{
  if (Serial.available() > 0) 
  {
    String data = Serial.readStringUntil('\n');
    if (data == "speed up")
      {
        if(speed < 250)
        {
          speed = speed + 10;
          speedR = speedR + 10;
          speedL = speedL + 10;
          analogWrite(pinR, speedR);
          analogWrite(pinL, speedL);
        }
        else
        {
          speed = 250;
          speedR = 250;
          speedL = 250;
          analogWrite(pinR, speedR);
          analogWrite(pinL, speedL);
        }
      }
    else if (data == "speed down")
      {
        if(speed > 0)
        {
          speed = speed - 10;
          speedR = speedR - 10;
          speedL = speedL - 10;
          analogWrite(pinR, speedR);
          analogWrite(pinL, speedL);
        }
        else
        {
          speed = 0;
          speedR = 0;
          speedL = 0;
          analogWrite(pinR, speedR);
          analogWrite(pinL, speedL);
        }
      }
    else if (data == "turn right")
      {

        Serial.print("You sent me: ");
        Serial.println(data);
      } 
    else if (data == "turn left")
      {

        Serial.print("You sent me: ");
        Serial.println(data);
      }
  }
}

void checkspeedR()
{
  timerR=millis();
  deltatimeR=timerR-prevtimerR;
  prevtimerR=timerR;
  
  freqR = 1.0/deltatimeR;
  
}
void checkspeedL()
{
  timerL=millis();
  deltatimeL=timerL-prevtimerL;
  prevtimerL=timerL;
  
  freqL = 1.0/deltatimeL;
  
}