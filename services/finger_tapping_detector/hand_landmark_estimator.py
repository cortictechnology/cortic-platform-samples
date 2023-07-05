"""
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021
"""

import coremltools as ct
import mediapipe_utils as mpu
import numpy as np
import cv2
import os

class HandLandmarkEstimator:
    def __init__(self):
        self.pd_input_width = 192
        self.pd_input_height = 192
        self.lm_input_width = 224
        self.lm_input_height = 224
        self.frame_size = 1280
        self.value = [0, 0, 0]
        self.borderType = cv2.BORDER_CONSTANT
        self.pd_score_thresh = 0.4
        self.pd_nms_thresh = 0.3
        self.lm_score_thresh = 0.5
        self.pad_h = 0
        self.pad_w = 0

        self.anchors = mpu.generate_handtracker_anchors(
            self.pd_input_width, self.pd_input_height
        )
        self.nb_anchors = self.anchors.shape[0]

        self.use_previous_landmarks = False
        self.hands_from_landmarks = []

        self.palm_input_node = "input_1"
        self.palm_model = ct.models.MLModel(
            os.path.dirname(os.path.realpath(__file__))
            + "/assets/palm_detection_full.mlmodel"
        )
        self.lm_input_node = "input_1"
        self.lm_model = ct.models.MLModel(
            os.path.dirname(os.path.realpath(__file__))
            + "/assets/hand_landmark_full.mlmodel"
        )

    def config_worker(self, params):
        pass

    def preprocess_input(self, image):
        self.h, self.w = image.shape[:2]
        self.frame_size = max(self.h, self.w)
        if self.h != self.w:
            self.pad_h = int((self.frame_size - self.h) / 2)
            self.pad_w = int((self.frame_size - self.w) / 2)
            square_image = cv2.copyMakeBorder(
                image,
                self.pad_h,
                self.pad_h,
                self.pad_w,
                self.pad_w,
                cv2.BORDER_CONSTANT,
            )

        img = cv2.resize(square_image, (self.pd_input_width, self.pd_input_height))
        img = np.divide(img, 255.0)
        img = img[..., ::-1]
        img = img[np.newaxis, :]
        img = np.ascontiguousarray(
            img,
            dtype=np.float32,
        )

        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img = img.astype("float32")
        # img = img / 255.0
        # img = img[np.newaxis, :]
        if not self.use_previous_landmarks:
            hands = self.get_palms(img)
        else:
            hands = self.hands_from_landmarks
        return hands, square_image

    def get_palms(self, image):
        hands = []
        if image is not None:
            result = self.palm_model.predict({self.palm_input_node: image})
            hands = self.pd_postprocess(result)
        return hands

    def pd_postprocess(self, data):
        # print(inference.getAllLayerNames())
        scores = np.squeeze(data["Identity_1"])
        bboxes = np.squeeze(data["Identity"])
        # bboxes = np.array(inference.getLayerFp16("Identity"), dtype=np.float16).reshape((self.nb_anchors,18))
        # Decode bboxes
        hands = mpu.decode_bboxes(
            self.pd_score_thresh,
            scores,
            bboxes,
            self.anchors,
            scale=self.pd_input_width,
            best_only=False,
        )
        # Non maximum suppression (not needed if solo)
        hands = mpu.non_max_suppression(hands, self.pd_nms_thresh)[:2]
        mpu.detections_to_rect(hands)
        mpu.rect_transformation(hands, self.frame_size, self.frame_size)
        return hands

    def lm_postprocess(self, hand, data):
        # print(inference.getAllLayerNames())
        # The output names of the landmarks model are :
        # Identity_1 (1x1) : score
        # Identity_2 (1x1) : handedness
        # Identity_3 (1x63) : world 3D landmarks (in meters)
        # Identity (1x63) : screen 3D landmarks (in pixels)
        this_hand = hand
        this_hand.lm_score = np.squeeze(data["Identity_1"])
        if this_hand.lm_score > self.lm_score_thresh:
            this_hand.handedness = np.squeeze(data["Identity_2"])
            lm_raw = np.squeeze(data["Identity"]).reshape(-1, 3)
            # hand.norm_landmarks contains the normalized ([0:1]) 3D coordinates of landmarks in the square rotated body bounding box
            this_hand.norm_landmarks = lm_raw / self.lm_input_width
            # hand.norm_landmarks[:,2] /= 0.4

            # Now calculate hand.landmarks = the landmarks in the image coordinate system (in pixel)
            src = np.array([(0, 0), (1, 0), (1, 1)], dtype=np.float32)
            dst = np.array(
                [(x, y) for x, y in hand.rect_points[1:]], dtype=np.float32
            )  # hand.rect_points[0] is left bottom point and points going clockwise!
            mat = cv2.getAffineTransform(src, dst)
            lm_xy = np.expand_dims(this_hand.norm_landmarks[:, :2], axis=0)
            # lm_z = hand.norm_landmarks[:,2:3] * hand.rect_w_a  / 0.4
            this_hand.landmarks = np.squeeze(cv2.transform(lm_xy, mat)).astype(int)
            this_hand.world_landmarks = np.squeeze(data["Identity_3"]).reshape(-1, 3)
        return this_hand

    def get_landmarks(self, hands, square_img):
        final_hands = []
        for i, h in enumerate(hands):
            img_hand = mpu.warp_rect_img(
                h.rect_points, square_img, self.lm_input_width, self.lm_input_height
            )
            img_hand = cv2.cvtColor(img_hand, cv2.COLOR_BGR2RGB)
            img_hand = img_hand.astype("float32")
            img_hand = img_hand / 255.0
            img_hand = img_hand[np.newaxis, :]
            result = self.lm_model.predict({self.lm_input_node: img_hand})
            h = self.lm_postprocess(h, result)
            if h.lm_score > self.lm_score_thresh:
                final_hands.append(h)
        for hand in final_hands:
            # If we added padding to make the image square, we need to remove this padding from landmark coordinates and from rect_points
            if self.pad_h > 0:
                hand.landmarks[:, 1] -= self.pad_h
                for i in range(len(hand.rect_points)):
                    hand.rect_points[i][1] -= self.pad_h
            if self.pad_w > 0:
                hand.landmarks[:, 0] -= self.pad_w
                for i in range(len(hand.rect_points)):
                    hand.rect_points[i][0] -= self.pad_w

            # Set the hand label
            hand.label = "left" if hand.handedness > 0.5 else "right"

        return final_hands

    def run_inference(self, img):
        hands, square_img = self.preprocess_input(img)
        # print(len(hands))
        hands = self.get_landmarks(hands, square_img)
        # print("***", len(hands))
        self.hands_from_landmarks = [mpu.hand_landmarks_to_rect(h) for h in hands]
        # nb_hands = len(hands)
        # self.use_previous_landmarks = True
        # if nb_hands == 0:
        #    self.use_previous_landmarks = False
        return hands
