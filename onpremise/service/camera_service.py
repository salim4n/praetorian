#connect to camera
import cv2
import datetime
import datetime
import service.blob_service as blob_service
import os

def run_camera():
    # make a five second video for testing
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 1, (640,480))
    start_time = datetime.datetime.now()
    while( datetime.datetime.now() - start_time < datetime.timedelta(seconds=5)):
        ret, frame = cap.read()
        if ret==True:
            out.write(frame)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    blob_service.upload_blob('output.avi', 'output.avi')
    # destroy output.avi after uploading to blob
    os.remove('output.avi')

def screenshot():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite('screenshot.png', frame)
    cap.release()
    cv2.destroyAllWindows()
