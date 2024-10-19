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
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

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


# If this is the main thread, simply start the server
if __name__ == '__main__':
	start_server()
