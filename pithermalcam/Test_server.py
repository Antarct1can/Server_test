from pi_therm_cam import pithermalcam
import cv2
from flask import Response, request
from flask import Flask
from flask import render_template
import threading
import time, socket, logging, traceback



# Set up Logger
logging.basicConfig(filename='pithermcam.log',filemode='a',
					format='%(asctime)s %(levelname)-8s [%(filename)s:%(name)s:%(lineno)d] %(message)s',
					level=logging.WARNING,datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)

# initialize the output frame and a lock used to ensure thread-safe exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
thermcam = None
current_camera = 1
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

@app.route('/change_camera')
def switch_camera():
    global thermal_camera, imx708_camera, usb_camera, current_camera
    thermal_camera = 1
    imx708_camera = 2
    usb_camera = 3
    current_camera = thermal_camera
    if current_camera == 1:
        current_camera = 2
    elif current_camera == 2:
        current_camera = 3
    elif current_camera == 3:
        current_camera = 1
    return "Camera switched."

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
	t.daemon = True
	t.start()

	ip=get_ip_address()
	port=8000

	print(f'Server can be found at {ip}:{port}')

	# start the flask app
	app.run(host=ip, port=port, debug=False,threaded=True, use_reloader=False)

def pull_images():
    global outputFrame, thermcam

    while True:
        if current_camera == thermal_camera:
            while thermcam is not None:
                current_frame=None
                try:
                    current_frame = thermcam.update_image_frame()
                except Exception:
                    print("Too many retries error caught; continuing...")

				# If we have a frame, acquire the lock, set the output frame, and release the lock
                if current_frame is not None:
                    with lock:
                        outputFrame = current_frame.copy()
        elif current_camera == imx708_camera:
            ret, frame = imx708_camera.read()
            # processed_frame = process_imx708_frame(frame)
        elif current_camera == usb_camera:
            ret, frame = usb_camera.read()
            # processed_frame = process_usb_frame(frame)


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

# If this is the main thread, simply start the server
if __name__ == '__main__':
    start_server()
