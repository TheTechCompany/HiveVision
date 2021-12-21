from typing import Tuple
import torch
import cv2
import requests
import time

telemetry = "http://192.168.255.62:4200/api/telemetry"

print("Loading YOLO...")
model = torch.hub.load('ultralytics/yolov3', 'yolov3')
print("Loaded model")
vid = cv2.VideoCapture(0)

while(True):

    print("Lesgo")
    ret, frame = vid.read()

    results = model(frame[..., ::-1])
    
    results.print()
    print("Wait then next")
    #print(results)

    #event, properties, source, timestamp 
    #x = requests.post(
    #    telemetry, 
    #    data={ 'event': 'camera-yolo', 'properties': results, 'source': 'camera', 'timestamp': time.time() })

    time.sleep(5)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

vid.release()


