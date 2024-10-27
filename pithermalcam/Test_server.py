from pi_therm_cam import pithermalcam
import cv2
import io
import libcamera
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import time
from flask import Response, request
from flask import Flask
from flask import render_template
import threading
import time, socket, logging, traceback

# board numbering system to use
#GPIO.setmode(GPIO.BOARD)

# variable to hold a short delay time
delayTime = 0.2

# setup trigger and echo pins
trigPin = 23
echoPin = 24
GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

# Set up Logger
logging.basicConfig(filename='pithermcam.log',filemode='a',
					format='%(asctime)s %(levelname)-8s [%(filename)s:%(name)s:%(lineno)d] %(message)s',
					level=logging.WARNING,datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

# initialize the output frame and a lock used to ensure thread-safe exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
thermcam = None
current_camera = 1
thermal_camera = 1
imx708_camera = 2
usb_camera = 3
dist_cm = 0
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index - Copy.html")  # Assuming your HTML file is named index.html

# @app.route("/video_feed")
# def video_feed():
# 	# return the response generated along with the specific media
# 	# type (mime type)
# 	return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/changeCameraBtn')
def switch_camera():
    global thermal_camera, imx708_camera, usb_camera, current_camera
    
    current_camera = thermal_camera
    if current_camera == 1:
        current_camera = 2
    elif current_camera == 2:
        current_camera = 3
    elif current_camera == 3:
        current_camera = 1
    return "Camera switched."


def distance_value():
    # start the pulse to get the sensor to send the ping
    while True:
        # set trigger pin low for 2 micro seconds
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
        #
        # divide in half since the time of travel is out and back
        dist_cm = (pingTravelTime*34444)/2
        # dist_inch = dist_cm * 0.3937008 # 1 cm = 0.3937008 inches
        print('Distance = ','inches |', round(dist_cm, 1),'cm')
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
    global outputFrame, thermcam, current_camera, capture_file

    while True:
        print (current_camera)
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
             #with libcamera.Camera() as camera:
             #    camera.configure(width=640, height=480)
    
             #    for _ in camera.capture_sequence([io.BytesIO()], format='jpeg'):
             #         outputframe = _.data
             with Picamera2() as camera:
                camera.start()
                camera.resolution = (640, 480)
                camera.framerate = 24
                stream = io.BytesIO()
                if current_frame is not None:
                    with lock:
                        outputFrame = capture(stream, format='jpeg')
                #for _ in camera.capture_file(stream):
                #    stream.seek(0)
                #    outputFrame = stream.read()
                #    stream.seek(0)
                #    stream.truncate()
                    
               # for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
               #     stream.seek(0)
               #     outputframe = stream.read()
                #    stream.seek(0)
                #    stream.truncate()
                
             ##with picamera2.Picamera2() as camera:
              #  camera.resolution = (640, 480)
              #  camera.framerate = 24
             #   stream = io.BytesIO()

              #  for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
              #      stream.seek(0)
               #     outputframe = stream.read()
              #      stream.seek(0)
               #     stream.truncate()
               
            #ret, frame = imx708_camera.read()
            # processed_frame = process_imx708_frame(frame)
        elif current_camera == usb_camera:
            ret, frame = usb_camera.read()
            # processed_frame = process_usb_frame(frame)


def generate_distance():
    global dist_cm

    while True:
        yield dist_cm

def generate():
    global outputFrame

    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

# # Modify the generate() function to provide camera feed frames
# def generate():
#     global outputFrame, lock
#     while True:
#         with lock:
#             if outputFrame is not None:
#                 # Encode the frame in JPEG format
#                 (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

#                 # Ensure the frame was successfully encoded
#                 if not flag:
#                     continue

#                 # Yield the output frame in the byte format
#                 yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
#                        bytearray(encodedImage) + b'\r\n')

# Update the video_feed route to return the camera feed frames
@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/dist_value")
def dist_value():
    distance_value()
    time.sleep(delayTime)
    return Response(generate_distance() , mimetype="text/plain")


# If this is the main thread, simply start the server
if __name__ == '__main__':
    print (dist_cm)
    start_server()
    
