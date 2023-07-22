import numpy as np
import math
from typing import List, Mapping, Optional, Tuple, Union


def denormalize_coordinates(
    normalized_x: float, normalized_y: float, image_width: int, image_height: int
) -> Union[None, Tuple[int, int]]:
    """Converts normalized value pair to pixel coordinates."""

    # Checks if the float value is between 0 and 1.
    def is_valid_normalized_value(value: float) -> bool:
        return (value > 0 or math.isclose(0, value)) and (
            value < 1 or math.isclose(1, value)
        )

    if not (
        is_valid_normalized_value(normalized_x)
        and is_valid_normalized_value(normalized_y)
    ):
        # TODO: Draw coordinates even if it's outside of the image bounds.
        return None
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px


def distance(point_1, point_2):
    """Calculate l2-norm between two points"""
    dist = sum([(i - j) ** 2 for i, j in zip(point_1, point_2)]) ** 0.5
    return dist


def get_ear(landmarks, refer_idxs, frame_width, frame_height):
    """
    Calculate Eye Aspect Ratio for one eye.

    Args:
        landmarks: (list) Detected landmarks list
        refer_idxs: (list) Index positions of the chosen landmarks
                            in order P1, P2, P3, P4, P5, P6
        frame_width: (int) Width of captured frame
        frame_height: (int) Height of captured frame

    Returns:
        ear: (float) Eye aspect ratio
    """
    try:
        # Compute the euclidean distance between the horizontal
        coords_points = []
        for i in refer_idxs:
            lm = landmarks[i]
            coord = denormalize_coordinates(lm[0], lm[1], frame_width, frame_height)
            coords_points.append(coord)

        # Eye landmark (x, y)-coordinates
        P2_P6 = distance(coords_points[1], coords_points[5])
        P3_P5 = distance(coords_points[2], coords_points[4])
        P1_P4 = distance(coords_points[0], coords_points[3])

        # Compute the eye aspect ratio
        ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)

    except:
        ear = 0.0
        coords_points = None

    return ear, coords_points


def calculate_avg_ear(landmarks, left_eye_idxs, right_eye_idxs, image_w, image_h):
    """Calculate Eye aspect ratio"""

    left_ear, left_lm_coordinates = get_ear(landmarks, left_eye_idxs, image_w, image_h)
    right_ear, right_lm_coordinates = get_ear(
        landmarks, right_eye_idxs, image_w, image_h
    )
    Avg_EAR = (left_ear + right_ear) / 2.0

    return Avg_EAR, (left_lm_coordinates, right_lm_coordinates)


def eye_converter(
    frame,
    video,
    left_eye_2d,
    right_eye_2d,
    face_center_p1_2d,
    face_center_p2_2d,
    warpped=False,
    left_eye_depth_mm=None,
    right_eye_depth_mm=None,
):
    p1 = face_center_p1_2d[:2]
    p2 = face_center_p2_2d[:2]
    # frame = cv2.line(frame, (int(p1[0] * video.frame_width), int(p1[1] * video.frame_height)), (int(p2[0] * video.frame_width), int(p2[1] * video.frame_height)), (0, 0, 255), 1)
    p3 = left_eye_2d[:2]
    p4 = right_eye_2d[:2]
    # frame = cv2.line(frame, (int(p3[0] * video.frame_width), int(p3[1] * video.frame_height)), (int(p4[0] * video.frame_width), int(p4[1] * video.frame_height)), (0, 255, 0), 1)

    denom = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
    origin_x = (
        (p1[0] * p2[1] - p1[1] * p2[0]) * (p3[0] - p4[0])
        - (p1[0] - p2[0]) * (p3[0] * p4[1] - p3[1] * p4[0])
    ) / denom
    origin_y = (
        (p1[0] * p2[1] - p1[1] * p2[0]) * (p3[1] - p4[1])
        - (p1[1] - p2[1]) * (p3[0] * p4[1] - p3[1] * p4[0])
    ) / denom
    # frame = cv2.circle(frame, (int(origin_x * video.frame_width), int(origin_y * video.frame_height)), 5, (255, 0, 0), -1)
    if warpped:
        left_eye_dist_px = np.sqrt(
            (
                ((p3[0] - origin_x) * video.frame_width) ** 2
                + ((p3[1] - origin_y) * video.frame_height) ** 2
            )
        )
        right_eye_dist_px = np.sqrt(
            (
                ((p4[0] - origin_x) * video.frame_width) ** 2
                + ((p4[1] - origin_y) * video.frame_height) ** 2
            )
        )
        # frame = cv2.putText(frame, f"{int(left_eye_dist_px)} px", (int(p3[0] * video.frame_width), int(p3[1] * video.frame_height) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255))
        # frame = cv2.putText(frame, f"{int(right_eye_dist_px)} px", (int(p4[0] * video.frame_width), int(p4[1] * video.frame_height) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255))
        # cv2.imshow("Eye distance (Warpped)", frame)
        return (left_eye_dist_px, right_eye_dist_px), None
    else:

        left_eye_dist_px = np.sqrt(
            (
                ((p3[0] - origin_x) * video.frame_width) ** 2
                + ((p3[1] - origin_y) * video.frame_height) ** 2
            )
        )
        right_eye_dist_px = np.sqrt(
            (
                ((p4[0] - origin_x) * video.frame_width) ** 2
                + ((p4[1] - origin_y) * video.frame_height) ** 2
            )
        )

        eye_dist_2d_px = left_eye_dist_px + right_eye_dist_px
        eye_dist_2d_mm = eye_dist_2d_px / video.focal_length * left_eye_depth_mm
        # print(eye_dist_2d_mm)

        eye_dist_mm = np.sqrt(
            eye_dist_2d_mm**2 + (left_eye_depth_mm - right_eye_depth_mm) ** 2
        )
        left_eye_dist_mm = left_eye_dist_px / eye_dist_2d_px * eye_dist_mm
        right_eye_dist_mm = eye_dist_mm - left_eye_dist_mm
        # frame = cv2.putText(frame, f"{int(left_eye_dist_px)}px, {int(left_eye_dist_mm)}mm", (int(p3[0] * video.frame_width) - 50, int(p3[1] * video.frame_height) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0))
        # frame = cv2.putText(frame, f"{int(right_eye_dist_px)}px, {int(right_eye_dist_mm)}mm", (int(p4[0] * video.frame_width), int(p4[1] * video.frame_height) + 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 0))
        # cv2.imshow("Eye distance (Unwarpped)", frame)
        return (left_eye_dist_px, right_eye_dist_px), (
            left_eye_dist_mm,
            right_eye_dist_mm,
        )
