from io import BytesIO
import os
import cv2
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()
azure_blob_account = os.getenv("AZURE_BLOB_ACCOUNT")

class RecordClass:
    def __init__(self,output_folder):
        self.output_folder = output_folder
        self.filename = f"{time.strftime('%Y%m%d%H%M%S')}.avi"
        self.filepath = os.path.join("onpremise/video_record", self.filename)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.filepath, self.fourcc, 20.0, (640, 480))
    
    def video_record(self, frame,isrecording):
        if isrecording:
            return
        else :
            print("Enregistrement d'une nouvelle vidéo.")
        self.out.write(frame)
    
    def finish_recording(self,frame):
        self.out.release()
        # Convertir l'image (numpy array) en un objet de flux de données
        ret, video_data = cv2.imencode('.jpg', frame)  # Note: .avi is not supported here
        if not ret:
            print("Erreur lors de l'encodage de la vidéo.")
            return
        video_stream = BytesIO(video_data.tobytes())
        print("\nUploading to Azure Storage as blob:\n\t" + self.filename)
        self.upload_video_blob(video_stream, self.filename)
        print("Suppression du fichier vidéo.")
        # Supprimer le fichier vidéo après l'avoir téléchargé
        os.remove(self.filepath)
    
    def upload_video_blob(self, video_stream, filename):
        connect_str = azure_blob_account
        blob_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_client.get_blob_client(container="onpremvideo", blob=filename)
        blob_client.upload_blob(video_stream)
        print("Vidéo envoyée avec succès.")

    def __call__(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        start_time = time.perf_counter()
        ret, frame = cap.read()
        while cap.isOpened():
            elapsed_time = time.perf_counter() - start_time
            ret, frame = cap.read()
            # Enregistre la vidéo si nécessaire
            if elapsed_time > 10:
                print("dans le if")
                print(elapsed_time)
                self.finish_recording(frame)
                self.video_record(frame,False)
            else: 
                print("dans le else")
                print( elapsed_time)
                self.video_record(frame,True)
            if ret == False:
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
# test
record = RecordClass(output_folder="onpremise/video_record")
record()
    