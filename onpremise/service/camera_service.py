from azure.storage.blob import BlobServiceClient
import cv2
import datetime
import os
from matplotlib.patches import draw_bbox
import torch
import numpy as np

connection_string = "DefaultEndpointsProtocol=https;AccountName=praetorianblob;AccountKey=PEv0rg+hl5Y2j4I52M6eddkBVK/1JghLJj95PfBtqC8F/T3bjKgfTwxxi6kGGPIvonrSLvvkI9Vc+AStNfJI6w==;EndpointSuffix=core.windows.net"

def upload_video_blob(data, filename):
    try:
        # Connect to the Azure storage account
        connect_str = connection_string
        blob_client = BlobServiceClient.from_connection_string(connect_str)
        print("\nUploading to Azure Storage as blob:\n\t" + filename)
        # Upload the created file
        blob_client = blob_client.get_blob_client(container="onpremvideo", blob=filename)
        blob_client.upload_blob(data)
            
    except Exception as ex:
        print('Exception:')
        print(ex)

def upload_blob(data, filename):
    try:
        # Connect to the Azure storage account
        connect_str = connection_string
        blob_client = BlobServiceClient.from_connection_string(connect_str)
        print("\nUploading to Azure Storage as blob:\n\t" + filename)
        # Upload the created file
        blob_client = blob_client.get_blob_client(container="onprempicture", blob=filename)
        blob_client.upload_blob(data)
            
    except Exception as ex:
        print('Exception:')
        print(ex)


def extract_frames(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def model_predict(model, preprocessor, frames):
    for frame in frames:
        # Assurez-vous que l'image a la forme appropriée
        if len(frame.shape) == 2:  # Si l'image est en niveaux de gris
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)  # Convertir en couleur

        # Redimensionner l'image à une taille compatible
        frame = cv2.resize(frame, (298, 223))

        frame = np.expand_dims(frame, axis=0)  # Ajouter une dimension de lot

        inputs = preprocessor(images=frame, return_tensors="pt",padding="max_length")
        outputs = model(**inputs)
        # model predicts bounding boxes and corresponding COCO classes
        logits = outputs.logits
        bboxes = outputs.pred_boxes
        # print results
        target_sizes = torch.tensor([[frame.shape[1], frame.shape[0]]] * outputs.logits.shape[0])  # Utiliser frame.shape pour obtenir les dimensions
        results = preprocessor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[0]
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            print(
                f"Detected {model.config.id2label[label.item()]} with confidence "
                f"{round(score.item(), 3)} at location {box}"
            )
    return results




def save_frames(frames, output_path):
    for i, frame in enumerate(frames):
        cv2.imwrite(os.path.join(output_path, f"{i}.jpg"), frame)
    print(f"Saved {len(frames)} frames to {output_path}")

def run_camera(model, preprocessor):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error opening video file")
        return
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        print("Predicting")
        results = model_predict(model, preprocessor, frame)
        print("Drawing boxes")
        image = draw_bbox(frame, results["boxes"], results["labels"], results["scores"])
        upload_blob(image, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg")
    cap.release()
    cv2.destroyAllWindows()
    print("Drawing boxes")
    print("Saving frames")





