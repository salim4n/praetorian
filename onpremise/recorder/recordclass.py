import os
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from io import BytesIO
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import time
import datetime
import os

load_dotenv()
output_folder_name = os.getenv("OUTPUT_FOLDER_NAME")
if not os.path.exists(output_folder_name):
    os.makedirs(output_folder_name)

class RecordClass:
    def __init__(self, output_folder, interval=20): # interval in seconds (default: 20)
        self.output_folder = output_folder
        self.interval = interval

    def __call__(self):
        # Initialize video capture
        cap = cv2.VideoCapture(0)
        # Get width and height of video frames
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        # Initialize video writer
        out = cv2.VideoWriter(f"{self.output_folder}/{datetime.datetime.now()}.avi", VideoWriter_fourcc(*'MJPG'), 10, (frame_width, frame_height))
        # Capture and write frames
        while True:
            start_time = time.time()
            frame_count = 0
            while time.time() - start_time <= self.interval:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    cv2.imshow('frame', frame)
                    frame_count += 1
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break

            # Release resources
            cap.release()
            out.release()
            cv2.destroyAllWindows()
# Usage
record = RecordClass(output_folder=f"{output_folder_name}")
record()