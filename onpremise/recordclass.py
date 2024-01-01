from io import BytesIO
import os
import cv2
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()
azure_blob_account = os.getenv("AZURE_BLOB_ACCOUNT")

class RecordClass:
    def __init__(self,output_folder):
        self.output_folder = output_folder
    
    def upload_video_blob(self, video_stream, filename):
        connect_str = azure_blob_account
        blob_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_client.get_blob_client(container="onpremvideo", blob=filename)
        blob_client.upload_blob(video_stream)
        print("Vidéo envoyée avec succès.")

    def __call__(self):
        #capture the webcam and save a video each 10 secondes
        cap = cv2.VideoCapture(0)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        out = VideoWriter('onpremise/video_record/outpy.avi', VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
        # Check if camera opened successfully
        if (cap.isOpened() == False):
            print("Unable to read camera feed")
        frame_count = 0
        while(True):
            ret, frame = cap.read()
            if ret == True:
                # Write the frame into the file 'output.avi'
                out.write(frame)
                # Display the resulting frame    
                cv2.imshow('frame', frame)
                frame_count += 1
                # Press Q on keyboard to stop recording
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                # If the number of captured frame is equal to 100, stop recording
                if frame_count == 100:
                    break
            # Break the loop
            else:
                break
        # When everything done, release the video capture and video write objects
        cap.release()
        out.release()
        # Closes all the frames
        cv2.destroyAllWindows()
        # Convertir l'image (numpy array) en un objet de flux de données
        video_data = open('onpremise/video_record/outpy.avi', 'rb')
        video_stream = video_data.read()
        video_data.close()
        video_stream = BytesIO(video_stream)
        filename = f"video_{time.strftime('%Y%m%d%H%M%S')}.avi"
        self.upload_video_blob(video_stream, filename)
        #os.remove(path="onpremise/video_record/outpy.avi")
    
# test
record = RecordClass(output_folder="onpremise/video_record")
record()
    