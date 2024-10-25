# Import libraries
import RPi.GPIO as GPIO
import time

#Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

#Set pin 11 as an output and set servo1 as pin 11 as PWM
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50)

#Start PWM running, but with value of 0 (pulse off)
servo1.start(1.5)
print("waiting for 2 seconds")
time.sleep(5)

for x in range(15, 125, 1):
	servo1.ChangeDutyCycle(x/10)
	print(x/10)
	time.sleep(0.1)
for x in range(125, 15, -1):
	servo1.ChangeDutyCycle(x/10)
	print(x/10)
	time.sleep(0.1)

#Clean things up at the end
servo1.stop()
GPIO.cleanup
print ("Goodbye")