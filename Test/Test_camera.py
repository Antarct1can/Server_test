from pithermalcam import pithermalcam
import threading
import time, socket, logging, traceback
import cv2

# # initialize the output frame and a lock used to ensure thread-safe exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
# outputFrame = None
# thermcam = None
# lock = threading.Lock()

def pull_images():
	global thermcam, outputFrame
	# loop over frames from the video stream
	while thermcam is not None:
		current_frame=None
		try:
			current_frame = thermcam.update_image_frame()
		except Exception:
			print("Too many retries error caught; continuing...")
			logger.info(traceback.format_exc())

		# If we have a frame, acquire the lock, set the output frame, and release the lock
		if current_frame is not None:
			with lock:
				outputFrame = current_frame.copy()

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')