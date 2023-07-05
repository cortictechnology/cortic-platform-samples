from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import numpy as np
import cv2
from face_detector import FaceDetector
from hand_landmark_estimator import HandLandmarkEstimator

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

FINGER_COLOR = [
    (128, 128, 128),
    (80, 190, 168),
    (234, 187, 105),
    (175, 119, 212),
    (81, 110, 221),
]

JOINT_COLOR = [(0, 0, 0), (125, 255, 79), (255, 102, 0), (181, 70, 255), (13, 63, 255)]


class FingerTappingDetector(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame}}
        self.output_type = {"frame": ServiceDataTypes.CvFrame, 
                            "faces": ServiceDataTypes.List,
                            "hand_infos": ServiceDataTypes.List}
        self.frame_capturer = None
        self.face_detect = None
        self.hand_landmark = None
        self.list_connections = [
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16],
            [17, 18, 19, 20],
        ]

    def activate(self):
        self.face_detect = FaceDetector()
        self.hand_landmark = HandLandmarkEstimator()
        log("FingerTappingDetector: <p style='color:blue'>Activated</p>")

    def draw_disconnected_rect(self, img, pt1, pt2, color, thickness):
        width = pt2[0] - pt1[0]
        height = pt2[1] - pt1[1]
        line_width = min(20, width // 4)
        line_height = min(20, height // 4)
        line_length = max(line_width, line_height)
        cv2.line(img, pt1, (pt1[0] + line_length, pt1[1]), color, thickness)
        cv2.line(img, pt1, (pt1[0], pt1[1] + line_length), color, thickness)
        cv2.line(
            img, (pt2[0] - line_length, pt1[1]), (pt2[0], pt1[1]), color, thickness
        )
        cv2.line(
            img, (pt2[0], pt1[1]), (pt2[0], pt1[1] + line_length), color, thickness
        )
        cv2.line(
            img, (pt1[0], pt2[1]), (pt1[0] + line_length, pt2[1]), color, thickness
        )
        cv2.line(
            img, (pt1[0], pt2[1] - line_length), (pt1[0], pt2[1]), color, thickness
        )
        cv2.line(img, pt2, (pt2[0] - line_length, pt2[1]), color, thickness)
        cv2.line(img, (pt2[0], pt2[1] - line_length), pt2, color, thickness)

    def norm2abs(self, x_y, frame_size, pad_w, pad_h):
        x = int(x_y[0] * frame_size - pad_w)
        y = int(x_y[1] * frame_size - pad_h)
        return (x, y)

    def draw_hand_landmarks(self, img, landmark_coordinates, handedness):
        palmar = False
        for lm_xy in landmark_coordinates:
            palm_line = [np.array([lm_xy[point] for point in [0, 5, 9, 13, 17, 0]])]
            if handedness > 0.5:
                # Simple condition to determine if palm is palmar or dorasl based on the relative
                # position of thumb and pinky finger
                if lm_xy[4][0] > lm_xy[20][0]:
                    cv2.polylines(
                        img, palm_line, False, (255, 255, 255), 2, cv2.LINE_AA
                    )
                else:
                    cv2.polylines(
                        img, palm_line, False, (128, 128, 128), 2, cv2.LINE_AA
                    )
            else:
                # Simple condition to determine if palm is palmar or dorasl based on the relative
                # position of thumb and pinky finger
                if lm_xy[4][0] < lm_xy[20][0]:
                    cv2.polylines(
                        img, palm_line, False, (255, 255, 255), 2, cv2.LINE_AA
                    )
                else:
                    cv2.polylines(
                        img, palm_line, False, (128, 128, 128), 2, cv2.LINE_AA
                    )

            # Draw line for each finger
            for i in range(len(self.list_connections)):
                finger = self.list_connections[i]
                line = [np.array([lm_xy[point] for point in finger])]
                if handedness > 0.5:
                    if lm_xy[4][0] > lm_xy[20][0]:
                        palmar = True
                        cv2.polylines(img, line, False, FINGER_COLOR[i], 2, cv2.LINE_AA)
                        for point in finger:
                            pt = lm_xy[point]
                            cv2.circle(img, (pt[0], pt[1]), 3, JOINT_COLOR[i], -1)
                    else:
                        palmar = False
                else:
                    if lm_xy[4][0] < lm_xy[20][0]:
                        palmar = True
                        cv2.polylines(img, line, False, FINGER_COLOR[i], 2, cv2.LINE_AA)
                        for point in finger:
                            pt = lm_xy[point]
                            cv2.circle(img, (pt[0], pt[1]), 3, JOINT_COLOR[i], -1)
                    else:
                        palmar = False

                # Use different colour for the hand to represent dorsal side
                if not palmar:
                    cv2.polylines(img, line, False, (128, 128, 128), 2, cv2.LINE_AA)
                    for point in finger:
                        pt = lm_xy[point]
                        cv2.circle(img, (pt[0], pt[1]), 3, (0, 0, 0), -1)
        return palmar

    def location_legit(self, location, for_width=True):
        if for_width:
            return location < self.context.get_state("frame_bound", 1280) and location >= 0
        else:
            return location < self.context.get_state("frame_bound", 720) and location >= 0

    def process(self, input_data=None):
        hand_infos = []
        detected_faces = []
        frame = input_data["camera_input"]["frame"]
        if frame.size == 0:
            frame = np.zeros((self.context.get_state("frame_height", 720), self.context.get_state("frame_width", 1280), 3), np.uint8)
        else:
            detected_faces = self.face_detect.run_inference(frame)
            hands = self.hand_landmark.run_inference(frame)
            for hand in hands:
                hand_info = {}
                hand_info["landmarks"] = hand.landmarks.tolist()
                hand_info["world_landmarks"] = hand.world_landmarks.tolist()
                hand_info["label"] = hand.label
                thumb = hand.world_landmarks[4]
                index = hand.world_landmarks[8]
                pinky = hand.world_landmarks[20]
                thumb_distance = (
                    np.linalg.norm(hand.world_landmarks[4] - hand.world_landmarks[0])
                    * 1000
                )
                index_distance = (
                    np.linalg.norm(hand.world_landmarks[8] - hand.world_landmarks[0])
                    * 1000
                )
                middle_distance = (
                    np.linalg.norm(hand.world_landmarks[12] - hand.world_landmarks[0])
                    * 1000
                )
                ring_distance = (
                    np.linalg.norm(hand.world_landmarks[16] - hand.world_landmarks[0])
                    * 1000
                )
                pinky_distance = (
                    np.linalg.norm(hand.world_landmarks[20] - hand.world_landmarks[0])
                    * 1000
                )
                hand_info["finger_distance"] = np.linalg.norm(thumb - index) * 1000
                hand_info["thumb_pinky_distance"] = np.linalg.norm(thumb - pinky) * 1000
                hand_info["middle_y_distance"] = hand.world_landmarks[12][1] * 1000
                hand_info["avg_finger_distance"] = (
                    thumb_distance
                    + index_distance
                    + middle_distance
                    + ring_distance
                    + pinky_distance
                ) / 5.0
                palmar = self.draw_hand_landmarks(
                    frame, [hand.landmarks.tolist()], hand.handedness
                )
                hand_info["palmar"] = palmar
                hand_infos.append(hand_info)
            for face in detected_faces:
                frame_width = frame.shape[1]
                frame_height = frame.shape[0]
                for face in detected_faces:
                    face_coordinates = face["face_coordinates"]
                    x1 = int(face_coordinates[0] * frame_width)
                    y1 = int(face_coordinates[1] * frame_height)
                    x2 = int(face_coordinates[2] * frame_width)
                    y2 = int(face_coordinates[3] * frame_height)
                    self.draw_disconnected_rect(
                        frame, (x1, y1), (x2, y2), (234, 187, 105), 2
                    )
        return {
            "frame": frame,
            "faces": detected_faces,
            "hand_infos": hand_infos
        }

    def deactivate(self):
        pass
