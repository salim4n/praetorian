# Description: This is the main file for the onPremise application
import service.camera_service as camera_service
from transformers import YolosImageProcessor, YolosForObjectDetection

def main():
    model = YolosForObjectDetection.from_pretrained("onpremise/service/yolos-tiny")
    preprocessor = YolosImageProcessor.from_pretrained("onpremise/service/yolos-tiny")
    camera_service.run_camera(model, preprocessor)
    camera_service.run_video(model, preprocessor, "onpremise/service/test.mp4")

if __name__ == "__main__":
    main()









