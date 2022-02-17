import torch
import json

model = torch.hub.load('ultralytics/yolov3', 'yolov3')

def find_object(frame):
    results = model(frame[..., ::-1])
    items = []
    for index, row in results.pandas().xyxy[0].iterrows():
        items.append(json.loads(row.to_json()))
    rows = list(filter(lambda x: x['confidence'] > 0.6, items))
    return rows