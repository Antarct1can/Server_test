from pi_therm_cam import pithermalcam
import cv2
import io
import serial
from libcamera import controls
import picamera2
from picamera2 import Picamera2
import RPi.GPIO as GPIO
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time
from flask import Response, request
from flask import Flask
from flask import render_template
import threading
import time, socket, logging, traceback


# variable to hold a short delay time
delayTime = 0.2

# setup trigger and echo pins
trigPin = 11
echoPin = 8
firePin = 16
upPin = 23
downPin = 23
rightPin = 24
leftPin = 24
brakePin1 = 17
brakePin2 = 27
GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)


fireFactory = PiGPIOFactory()
fireServo = Servo(firePin, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000, pin_factory = fireFactory)
fireServo.value = None;

upFactory = PiGPIOFactory()
upServo = Servo(upPin, min_pulse_width = 0.4/1000, max_pulse_width = 2.6/1000, pin_factory = upFactory)
upServo.value = None;

downFactory = PiGPIOFactory()
downServo = Servo(downPin, min_pulse_width = 0.4/1000, max_pulse_width = 2.6/1000, pin_factory = downFactory)
downServo.value = None;

rightFactory = PiGPIOFactory()
rightServo = Servo(rightPin, min_pulse_width = 0.4/1000, max_pulse_width = 2.6/1000, pin_factory = rightFactory)
rightServo.value = None;

leftFactory = PiGPIOFactory()
leftServo = Servo(leftPin, min_pulse_width = 0.4/1000, max_pulse_width = 2.6/1000, pin_factory = leftFactory)
leftServo.value = None;

brake1Factory = PiGPIOFactory()
brake1Servo = Servo(brakePin1, min_pulse_width = 0.4/1000, max_pulse_width = 2.6/1000, pin_factory = brake1Factory)
brake1Servo.value = None;

brake2Factory = PiGPIOFactory()
brake2Servo = Servo(brakePin2, min_pulse_width = 0.4/1000, max_pulse_width = 2.6/1000, pin_factory = brake2Factory)
brake2Servo.value = None;

# Set up Logger
logging.basicConfig(filename='pithermcam.log',filemode='a',
					format='%(asctime)s %(levelname)-8s [%(filename)s:%(name)s:%(lineno)d] %(message)s',
					level=logging.WARNING,datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

# initialize the output frame and a lock used to ensure thread-safe exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
RGBFrame = None
thermcam = None
ser = None
thermal_camera = 1
imx708_camera = 2
usb_camera = 3
current_camera = 1
dist_cm = 0
updown_value = 0
rightleft_value = 0
toggle_brake = 0
lock = threading.Lock()


camera1 = Picamera2()
camera1.configure(camera1.create_video_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera1.set_controls({"AfMode": controls.AfModeEnum.Continuous})

video_capture = cv2.VideoCapture(0)
video_result = None
    
# initialize a flask object
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index - Copy.html")  # Assuming your HTML file is named index.html


@app.route('/changeCameraBtn')
def switch_camera():
    global thermal_camera, imx708_camera, usb_camera, current_camera
    
    if current_camera == thermal_camera:
        current_camera = imx708_camera
        camera1.start()
        
    elif current_camera == imx708_camera:
        current_camera = usb_camera
        camera1.stop()
    elif current_camera == usb_camera:
        current_camera = thermal_camera
    return "Camera switched."

@app.route('/fireBtn')
def firebutton():    
    fireServo.max()
    time.sleep(0.5)
    fireServo.min()
    time.sleep(0.5)
    fireServo.value = None;
    return "Weapon fired"

@app.route('/upBtn')
def upbutton():
    global updown_value

    if updown_value < 10:
        upServo.value = updown_value/10
        time.sleep(0.1)
        #print("up")
        updown_value = updown_value + 1
        return "Weapon up"
    else:
        return "Max pitch"
    
@app.route('/downBtn')
def downbutton():    
    global updown_value
    
    if updown_value > -10:
        downServo.value = updown_value/10
        time.sleep(0.1)
        #print("down")
        updown_value = updown_value - 1
        return "Weapon down"
    else:
        return "Min pitch"
    
@app.route('/rightBtn')
def rightbutton():
    global rightleft_value
    
    if rightleft_value > -10:
        rightServo.value = rightleft_value/10
        time.sleep(0.1)
        #print("right")
        rightleft_value = rightleft_value - 1
        return "Weapon right"
    else:
        return "Max yaw"    
    
@app.route('/leftBtn')
def leftbutton():    
    global rightleft_value
    
    if rightleft_value < 10:
        leftServo.value = rightleft_value/10
        time.sleep(0.1)
        #print("left")
        rightleft_value = rightleft_value + 1
        return "Weapon left"
    else:
        return "Min yaw"   
    
@app.route('/wBtn')
def wbutton():
    global ser
    print("meow")
    ser.write(b"speed up\n")
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)
    return "Speed up"

@app.route('/sBtn')
def sbutton():
    global ser
    ser.write(b"speed down\n")
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)
    return "Speed down"

@app.route('/dBtn')
def dbutton():
    global ser
    ser.write(b"speed right\n")
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)
    return "Wheel right"

@app.route('/aBtn')
def abutton():
    global ser
    ser.write(b"speed left\n")
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)
    return "Wheel left"

@app.route('/brakeBtn')
def brakebutton():
    global toggle_brake   
    if toggle_brake == 0:
        brake1Servo.max()
        brake2Servo.max()
        time.sleep(0.1)
        toggle_brake = 1
    elif toggle_brake == 1:
        brake1Servo.min()
        brake2Servo.min()
        time.sleep(0.1)
        toggle_brake = 0
    return "Brake"
    



def distance_value():
    global dist_cm
    # start the pulse to get the sensor to send the ping
    while True:
        time.sleep(delayTime)
        # set trigger pin low for 2 micro secondsF
        GPIO.output(trigPin, 0)
        time.sleep(2E-6)
        # set trigger pin high for 10 micro seconds
        GPIO.output(trigPin, 1)
        time.sleep(10E-6)
        # go back to zero - communication compete to send ping
        GPIO.output(trigPin, 0)
        # now need to wait till echo pin goes high to start the timer
        # this means the ping has been sent
        while GPIO.input(echoPin) == 0:
            pass
        # start the time - use system time
        echoStartTime = time.time()
        # wait for echo pin to go down to zero
        while GPIO.input(echoPin) == 1:
            pass
        echoStopTime = time.time()
        # calculate ping travel time
        pingTravelTime = echoStopTime - echoStartTime
        # Use the time to calculate the distance to the target.
        # speed of sound at 72 deg F is 344.44 m/s
        # from weather.gov/epz/wxcalc_speedofsound.
        # equations used by calculator at website above.
        # speed of sound = 643.855*((temp_in_kelvin/273.15)^0.5)
        # temp_in_kelvin = ((5/9)*(temp_in_F - 273.15)) + 32

        # divide in half since the time of travel is out and back
        dist_cm = (pingTravelTime*34444)/2
        dist_cm = round(dist_cm, 2)
        # sleep to slow things down
        time.sleep(delayTime)

def get_ip_address():
    """Find the current IP address of the device"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address=s.getsockname()[0]
    s.close()
    return ip_address

def start_server(output_folder:str = '/home/pi/pithermalcam/saved_snapshots/'):
        global thermcam
        # initialize the video stream and allow the camera sensor to warmup
        thermcam = pithermalcam(output_folder=output_folder)
        time.sleep(0.1)

        # start a thread that will perform motion detection
        t = threading.Thread(target=pull_images)
        t2 = threading.Thread(target=distance_value)
        t.daemon = True
        t.start()
        t2.daemon = True
        t2.start()

        ip=get_ip_address()
        port=8000

        print(f'Server can be found at {ip}:{port}')

        # start the flask app
        app.run(host=ip, port=port, debug=False,threaded=True, use_reloader=False)

def pull_images():
    global outputFrame, thermcam, current_camera, RGBFrame, video_frame, video_result
    #indextest = 0
    while True:
        #print (current_camera)
        #indextest = indextest + 1
        if current_camera == thermal_camera:
            current_frame=None
            try:
                current_frame = thermcam.update_image_frame()
            except Exception as e:
                print (e)
                print("Too many retries error caught; continuing...")

            # If we have a frame, acquire the lock, set the output frame, and release the lock
            if current_frame is not None:
                with lock:
                    outputFrame = current_frame.copy()
                    
                    
        elif current_camera == imx708_camera:
            #with lock:
            RGBFrame = camera1.capture_array()
                
        elif current_camera == usb_camera:
            video_result, video_frame = video_capture.read()  # read frames from the video


def generate_distance():
    global dist_cm
    while True:
        yield ("{}\n".format(dist_cm))



def generate():
    global outputFrame, RGBFrame, video_frame, video_result

    while True:
        if current_camera == thermal_camera:
            with lock:
                if outputFrame is None:
                    continue
                (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
                if not flag:
                    continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
            
        elif current_camera == imx708_camera:
            #with lock:
                
            if RGBFrame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', RGBFrame)
            if not ret:
                continue
            rgbFrame = bytearray(buffer)

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + rgbFrame + b'\r\n')
        
        elif current_camera == usb_camera:
            if video_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', video_frame )
            if ret is False:
                continue
            usbFrame = bytearray(buffer)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + usbFrame + b'\r\n')

# Update the video_feed route to return the camera feed frames
@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

    
@app.route("/dist_value")
def dist_value():
    global dist_cm
    return Response(generate_distance() , mimetype="text/plain")


# If this is the main thread, simply start the server
if __name__ == '__main__':
    start_server()
    ser = serial.Serial('/dev/ttyACM0', 400000, timeout=1)
    ser.reset_input_buffer()
    
