import os
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from io import BytesIO
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import time

load_dotenv()
azure_blob_account = os.getenv("AZURE_BLOB_ACCOUNT")
output_folder_name = "video_record"
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
        out = VideoWriter(f'{output_folder_name}/outpy.avi', VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

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

            # Read saved video and prepare for upload
            video_data = open(f'{output_folder_name}/outpy.avi', 'rb')
            video_stream = BytesIO(video_data.read())
            video_data.close()

            # Generate unique filename
            filename = f"{self.output_folder}/{time.strftime('%Y%m%d%H%M%S')}_video.avi"

            # Upload video to Azure Blob Storage
            self.upload_video_blob(video_stream, filename)
            # Remove saved video
            os.remove(path=f"{output_folder_name}/outpy.avi")

    def upload_video_blob(self, video_stream, filename):
        print("Envoi de la vidéo...")
        blob_client = BlobServiceClient.from_connection_string(azure_blob_account)
        blob_client = blob_client.get_blob_client(container="onpremvideo", blob=filename)
        blob_client.upload_blob(video_stream)
        print("Vidéo envoyée avec succès.")

# Usage
record = RecordClass(output_folder=f"{output_folder_name}")
record()