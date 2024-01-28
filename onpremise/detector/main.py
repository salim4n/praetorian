import time
from detrclass import DETRClass

def run_detector(output_folder_detect):
    """Runs person detection and takes screenshots upon detection."""
    detector = DETRClass(output_folder_detect)
    while True:
        detector()
        time.sleep(5)

if __name__ == "__main__":
    output_folder_detect = "onpremise/detector/screenshot/"
    run_detector(output_folder_detect)