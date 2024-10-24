from pithermalcam import pithermalcam
import cv2
import threading
from flask import Flask, Response

app = Flask(__name__)

thermal_camera = pithermalcam(output_folder='/home/pi/pithermalcam/saved_snapshots/')
imx708_camera = cv2.VideoCapture(0)  # Adjust the index based on the camera device
usb_camera = cv2.VideoCapture(1)  # Adjust the index based on the camera device
current_camera = thermal_camera

lock = threading.Lock()
outputFrame = None

@app.route('/')
def index():
    return "Hello, World! <a href='/video_feed'>Watch Video Feed</a>"

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
            processed_frame = process_imx708_frame(frame)
        elif current_camera == usb_camera:
            ret, frame = usb_camera.read()
            processed_frame = process_usb_frame(frame)

        with lock:
            outputFrame = processed_frame.copy()

# def process_thermal_frame(frame):
#     # Process raw pixel data from the thermal camera
#     thermal_image = cv2.applyColorMap(frame, cv2.COLORMAP_JET)  # Example processing
#     return thermal_image

def process_imx708_frame(frame):
    # Process frames from the IMX708 camera
    # Add your processing logic here
    return frame

def process_usb_frame(frame):
    # Process frames from the USB camera
    # Add your processing logic here
    return frame

# def generate():
#     global outputFrame

#     while True:
#         with lock:
#             if outputFrame is None:
#                 continue
#             (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
#             if not flag:
#                 continue

#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')



if __name__ == '__main__':
    t = threading.Thread(target=pull_images)
    t.daemon = True
    t.start()

    app.run(host='0.0.0.0', port=5000, debug=True)