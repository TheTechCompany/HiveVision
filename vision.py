import torch
import cv2

print("Loading YOLO...")
model = torch.hub.load('ultralytics/yolov3', 'yolov3')
print("Loaded model")
vid = cv2.VideoCapture(0)

while(True):

    ret, frame = vid.read()

    results = model(frame)
    
    cv2.imshow('frame', frame)

    results.print()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

vid.release()


