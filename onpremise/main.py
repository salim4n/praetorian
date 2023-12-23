# Description: This is the main file for the onPremise application
import service.blob_service as blob_service
import service.camera_service as camera_service



def main():
    camera_service.run_camera()

if __name__ == "__main__":
    main()








