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
volatile int centered = 0;
volatile int position = 0;
volatile int notRight = 0;

int pinR = 5;
int pinL = 6;
int pinreadingR = 2;
int pinreadingL = 3;
int pinDirection = 12;
int pinTurn = 13;
int pinPosition = 11;

void setup() 
{
  Serial.begin(400000);
  pinMode(pinR,OUTPUT);
  pinMode(pinL,OUTPUT);
  pinMode(pinreadingR,INPUT);
  pinMode(pinreadingL,INPUT);
  pinMode(pinDirection,OUTPUT);
  pinMode(pinTurn,OUTPUT);
  pinMode(pinPosition,INPUT);
  
  attachInterrupt(digitalPinToInterrupt(pinreadingR), checkspeedR, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinreadingL), checkspeedL, FALLING);

  speed = constrain(speed,0,255);
  speedR = constrain(speedR,0,255);
  speedL = constrain(speedL,0,255);
  readingR = constrain(readingR,0,255);
  readingL = constrain(readingL,0,255);

  while(centered != 1 || notRight != 1)
  {
    position = digitalRead(pinPosition);
    if(position == LOW)
    {
      digitalWrite(pinDirection,HIGH);
      digitalWrite(pinTurn,LOW);
      digitalWrite(pinTurn,HIGH);
      delayMicroseconds(60);
    }
    else
    {
      centered = 1;
    }
  }
  while(centered != 1)
  {
    position = digitalRead(pinPosition);
    if(position == LOW)
    {
      digitalWrite(pinDirection,LOW);
      digitalWrite(pinTurn,LOW);
      digitalWrite(pinTurn,HIGH);
      delayMicroseconds(60);
    }
    else
    {
      centered = 1;
    }
  }
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
      }
    else if (data == "turn right")
      {
        for(int i=0;i<500;i++)
        {
          digitalWrite(pinDirection,HIGH);
          digitalWrite(pinTurn,LOW);
          digitalWrite(pinTurn,HIGH);
          delayMicroseconds(60);
        }
      } 
    else if (data == "turn left")
      {
       for(int j=0;j<500;j++)
        {
          digitalWrite(pinDirection,LOW);
          digitalWrite(pinTurn,LOW);
          digitalWrite(pinTurn,HIGH);
          delayMicroseconds(60);
        }
      }
  }
}

void checkspeedR()
{
  timerR=millis();
  deltatimeR=timerR-prevtimerR;
  prevtimerR=timerR;
  
  freqR = 1.0/deltatimeR;
  readingR = map(freqR,0,125,0,255);
  if (readingR != speed)
  {
    speedR = readingR + (speed - readingR);
    analogWrite(pinR, speedR);
  }
}
void checkspeedL()
{
  timerL=millis();
  deltatimeL=timerL-prevtimerL;
  prevtimerL=timerL;
  
  freqL = 1.0/deltatimeL;
  readingL = map(freqL,0,125,0,255);
  if (readingL != speed)
  {
    speedL = readingL + (speed - readingL);
    analogWrite(pinL, speedL);
  }
}