import threading
import cv2
import time
import json
import requests
# from spectacles.hands.index import find_hands
from spectacles.objects.index import find_object

telemetry = "http://hahei-jumpbox.hexhive.io/api/telemetry"

class Spectacle:

    def __init__(self):
        self.thread = None
        self.camera = cv2.VideoCapture(0)
        self.currentTime = 0
        self.lastTime = 0
        self.currentPosition = {'gesture': '', 'position': [0, 0, 0, 0]}
    
    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._capture)
            self.thread.start()

    def get_pos(self):
        return self.currentPosition

    def _long_capture(self, frame):
            objects = find_object(frame)
            requests.post(
                telemetry,      
                headers={'content-type': 'application/json'},
                data=json.dumps({'event': 'camera-yolo', 'properties': {'results': objects}, 'source': 'camera', 'timestamp': time.time() * 1000}))

    def _capture(self):
        while(True):

            self.currentTime = time.time()

            ret, frame = self.camera.read()

            debug_image = cv2.flip(frame, 1)
        
            # bounds, hand = find_hands(frame)

            if self.currentTime - self.lastTime > 5:
                capture = threading.Thread(target=self._long_capture, args=([frame]))
                capture.start()
                self.lastTime = self.currentTime


            # self.currentPosition = {'gesture': hand, 'position': bounds}
    
            # print(hand)

            time.sleep(0.2)

            # if cv2.waitKey(200) & 0xFF == ord('q'):
            #     break

    # cv2.destroyAllWindows()

    # vid.release()