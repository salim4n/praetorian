from io import BytesIO
import torch
import numpy as np
import cv2
import time
import supervision as sv
from ultralytics import RTDETR
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()
azure_blob_account = os.getenv("AZURE_BLOB_ACCOUNT")

class DETRClass:
    def __init__(self, capture_index, detection_interval, output_folder):
        self.capture_index = capture_index
        self.device = torch.hdevice = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        self.model = RTDETR("rtdetr-l.pt").to(self.device)
        self.CLASS_NAMES_DICT = self.model.model.names
        print(f"Classes: {self.CLASS_NAMES_DICT}")
        self.detection_interval = detection_interval
        self.frame_count = 0
        self.output_folder = output_folder

    def save_screenshot(self, frame, label):
        filename = f"{label}_{time.strftime('%Y%m%d%H%M%S')}.png"
        filepath = os.path.join(self.output_folder, filename)
        cv2.imwrite(filepath, frame)
        # Convertir l'image (numpy array) en un objet de flux de données
        image_data = cv2.imencode('.png', frame)[1].tobytes()
        image_stream = BytesIO(image_data)
        connect_str = azure_blob_account
        blob_client = BlobServiceClient.from_connection_string(connect_str)
        print("\nUploading to Azure Storage as blob:\n\t" + filename)
        # Upload le flux de données seulement si la personne est détectée
        blob_client = blob_client.get_blob_client(container="onprempicture", blob=filename)
        blob_client.upload_blob(image_stream)
        os.remove(path="onpremise/screenshot/"+filename)

    def plot_bboxes(self, results, frame):
        boxes = results[0].boxes.cpu().numpy()
        class_id = boxes.cls
        conf = boxes.conf
        xyxy = boxes.xyxy
        class_id = class_id.astype(np.int32)
        detections = sv.Detections(xyxy=xyxy, class_id=class_id, confidence=conf)
        for xyxy, mask, confidence, class_id, track_id in detections:
            label = f"{self.CLASS_NAMES_DICT[class_id]}_{confidence:.2f}"
            # Vérifie si la personne est détectée avant d'écrire sur l'image
            if class_id == 0:
                # Récupère les coordonnées du coin supérieur gauche de la boîte
                x, y = int(xyxy[0]), int(xyxy[1])
                # Ajoute le texte à l'image à l'emplacement de la détection
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                # Enregistre l'image si nécessaire
                self.save_screenshot(frame, label)

        return frame
    
    def __call__(self):
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened(), f"Failed to open capture {self.capture_index}"
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        start_time = time.perf_counter()
        while cap.isOpened():
            ret, frame = cap.read()
            # Detection sur chaque N trames
            if self.frame_count % self.detection_interval == 0:
                results = self.model.predict(frame)
                frame = self.plot_bboxes(results, frame)
            end_time = time.perf_counter()
            fps = 1.0 / (end_time - start_time)
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("DETR", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            self.frame_count += 1
        cap.release()
        cv2.destroyAllWindows()

# Exemple d'utilisation et test
transformer_detector = DETRClass(0, detection_interval=100, output_folder="onpremise/screenshot")
transformer_detector()
