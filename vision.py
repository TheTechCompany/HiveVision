import torch
import cv2
import json

telemetry = "http://192.168.255.62:4200/api/telemetry"

print("Loading YOLO...")
model = torch.hub.load('ultralytics/yolov3', 'yolov3')
print("Loaded model")
vid = cv2.VideoCapture(0)
print("Grabbed camera")

while(True):

    print("Lesgo")
    ret, frame = vid.read()

    results = model(frame[..., ::-1])

    items = []
    
    for index, row in results.pandas().xyxy[0].iterrows():
        items.append(json.loads(row.to_json()))

    rows = list(filter(lambda x: x['confidence'] > 0.6, items))
    # print(results.pandas().xyxy[0].loc[0].to_json())
    #print("Wait then next")
    print(rows)
    #print(results)

    #event, properties, source, timestamp 
    #x = requests.post(
    #    telemetry, 
    #    data={ 'event': 'camera-yolo', 'properties': results, 'source': 'camera', 'timestamp': time.time() })

    #time.sleep(5)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

vid.release()


