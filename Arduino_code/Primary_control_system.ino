volatile float speed = 0;
volatile float speedR = 0;
volatile float speedL = 0;
volatile float readingR = 0;
volatile float readingL = 0;
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
int pinStartR = 9;
int pinStartL = 10;

void setup() 
{
  Serial.begin(400000);
  
  TCCR0B = TCCR0B & B11111000 | B00000001; // pins 5 and 6 PWM Frequency 62.5 khz
  TCCR1B = TCCR1B & B11111000 | B00000001;

  TCCR1B = (TCCR1B & 0b11111000) | 0x01; //pins 9 and 10 PWM Frequency 50 hz
  
  pinMode(pinR,OUTPUT);
  pinMode(pinL,OUTPUT);
  pinMode(pinreadingR,INPUT);
  pinMode(pinreadingL,INPUT);
  pinMode(pinDirection,OUTPUT);
  pinMode(pinTurn,OUTPUT);
  pinMode(pinPosition,INPUT);
  pinMode(pinStartR,OUTPUT);
  pinMode(pinStartL,OUTPUT);
  
  attachInterrupt(digitalPinToInterrupt(pinreadingR), checkspeedR, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinreadingL), checkspeedL, FALLING);

  speed = constrain(speed,61,102);
  speedR = constrain(speedR,61,102);
  speedL = constrain(speedL,61,102);
  readingR = constrain(readingR,0,102);
  readingL = constrain(readingL,0,102);

  speed = 61;
  speedR = 61;
  speedL = 61;
  analogWrite(pinR, speedR);
  analogWrite(pinL, speedL);


//  while(centered != 1 || notRight != 1)
//  {
//    position = digitalRead(pinPosition);
//    if(position == LOW)
//    {
//      digitalWrite(pinDirection,HIGH);
//      digitalWrite(pinTurn,LOW);
//      digitalWrite(pinTurn,HIGH);
//      delayMicroseconds(100000);
//      digitalWrite(pinTurn,LOW);
//    }
//    else
//    {
//      centered = 1;
//    }
//  }
//  while(centered != 1)
//  {
//    position = digitalRead(pinPosition);
//    if(position == LOW)
//    {
//      digitalWrite(pinDirection,LOW);
//      digitalWrite(pinTurn,LOW);
//      digitalWrite(pinTurn,HIGH);
//      delayMicroseconds(60);
//    }
//    else
//    {
//      centered = 1;
//    }
//  }
}

void loop() 
{
  if (Serial.available() > 0) 
  {
    String data = Serial.readStringUntil('\n');
    if (data == "speed up")
      {
        if(speed < 102)
        {
          speed = speed + 1.64;
          speedR = speedR + 1.64;
          speedL = speedL + 1.64;
          analogWrite(pinR, speedR);
          analogWrite(pinL, speedL);
          if(speed == 61)
          {
            analogWrite(pinStartR, 128);
            analogWrite(pinStartL, 128);
            delayMicroseconds(100000);
            analogWrite(pinStartR, 0);
            analogWrite(pinStartL, 0);
          }
        }
      }
    else if (data == "speed down")
      {
        if(speed > 61)
        {
          speed = speed - 1.64;
          speedR = speedR - 1.64;
          speedL = speedL - 1.64;
          analogWrite(pinR, speedR);
          analogWrite(pinL, speedL);
        }
      }
    else if (data == "turn right")
      {
        for(int i=0;i<50;i++)
        {
          digitalWrite(pinDirection,HIGH);
          digitalWrite(pinTurn,LOW);
          digitalWrite(pinTurn,HIGH);
          digitalWrite(pinTurn,LOW);
          delayMicroseconds(100000);
        }
      } 
    else if (data == "turn left")
      {
       for(int j=0;j<50;j++)
        {
          digitalWrite(pinDirection,LOW);
          digitalWrite(pinTurn,LOW);
          digitalWrite(pinTurn,HIGH);
          digitalWrite(pinTurn,LOW);
          delayMicroseconds(100000);
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
    speedR = speedR + (speed - readingR);
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
    speedL = speedL + (speed - readingL);
    analogWrite(pinL, speedL);
  }
}
