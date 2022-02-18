from collections import deque
from collections import Counter
from pathlib import Path
import itertools
import copy
import csv
import cv2
import mediapipe as mp
import numpy as np
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


from .model import KeyPointClassifier
from .model import PointHistoryClassifier

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

keypoint_classifier = KeyPointClassifier()
point_history_classifier = PointHistoryClassifier()

kp_classifier_label_loc = Path('spectacles/hands/model/keypoint_classifier/keypoint_classifier_label.csv')
p_classifier_label_loc = Path('spectacles/hands/model/point_history_classifier/point_history_classifier_label.csv')

with open(kp_classifier_label_loc,
            encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]

with open(p_classifier_label_loc,
            encoding='utf-8-sig') as f:
    point_history_classifier_labels = csv.reader(f)
    point_history_classifier_labels = [row[0] for row in point_history_classifier_labels]

history_length = 16
point_history = deque(maxlen=history_length)

finger_gesture_history = deque(maxlen=history_length)

mode = 0

def find_hands(frame):

    image = cv2.flip(frame, 1)    
    debug_image = copy.deepcopy(image)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    bounds = []

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True

    if results.multi_hand_landmarks is not None:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):

            brect = calc_bounding_rect(debug_image, hand_landmarks)

            bounds.append(brect)

            landmark_list = calc_landmark_list(debug_image, hand_landmarks)

            pre_processed_landmark_list = pre_process_landmark(
                landmark_list
            )

            pre_processed_point_history_list = pre_process_point_history(
                debug_image, point_history
            )

            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
            
            if hand_sign_id == 2:
                point_history.append(landmark_list[8])
            else:
                point_history.append([0, 0])

            finger_gesture_id = 0
            point_history_len = len(pre_processed_point_history_list)

            if point_history_len == (history_length * 2):
                finger_gesture_id = point_history_classifier(
                    pre_processed_point_history_list
                )

            finger_gesture_history.append(finger_gesture_id)

            most_common_fg_id = Counter(
                finger_gesture_history
            ).most_common()

            return bounds, keypoint_classifier_labels[hand_sign_id]

    else:
        point_history.append([0, 0])
        return [], 'no_hand'

    #     keypoint_classifier_labels[hand_sign_id]
    # return point_history, finger_gesture_history, bounds



def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv2.boundingRect(landmark_array)

    return [x, y, x + w, y + h]



def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # キーポイント
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # 相対座標に変換
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # 1次元リストに変換
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # 正規化
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # 相対座標に変換
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # 1次元リストに変換
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history
