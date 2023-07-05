# Service is implemented based on this sample code:
# https://github.com/googlesamples/mediapipe/blob/main/examples/face_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Face_Landmarker.ipynb

from cortic_platform.sdk.service import Service
from cortic_platform.sdk.logging import log, LogLevel
from cortic_platform.sdk.service_data_types import ServiceDataTypes
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

# Uncomment the following lines to enable debugpy so that you can attach a debugger to the app
# in VSCode. A vscode configuration is already provided in the .vscode folder. You will need to
# make sure the port in the vscode configuration is the same as the one specified in the
# debugpy.listen() call.

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5


def process_result(rgb_image, detection_result, draw_landmarks=True):
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)
    all_face_landmarks = []

    # Loop through the detected faces to visualize.
    for idx in range(len(face_landmarks_list)):
        face_landmarks = face_landmarks_list[idx]
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
        ])
        landmarks = []
        for idx, landmark in enumerate(face_landmarks_proto.landmark):
            if ((landmark.HasField('visibility') and
                landmark.visibility < _VISIBILITY_THRESHOLD) or
                (landmark.HasField('presence') and
                    landmark.presence < _PRESENCE_THRESHOLD)):
                continue
            landmarks.append(
                [landmark.x, landmark.y, landmark.z])
        all_face_landmarks.append(landmarks)

        if draw_landmarks:
            # Draw the face landmarks.
            solutions.drawing_utils.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks_proto,
                connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp.solutions.drawing_styles
                .get_default_face_mesh_tesselation_style())
            solutions.drawing_utils.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks_proto,
                connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp.solutions.drawing_styles
                .get_default_face_mesh_contours_style())
            solutions.drawing_utils.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks_proto,
                connections=mp.solutions.face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp.solutions.drawing_styles
                .get_default_face_mesh_iris_connections_style())

    return annotated_image, np.array(all_face_landmarks)


class FaceLandmarks(Service):
    def __init__(self):
        super().__init__()
        self.input_type = {"camera_input": {"frame": ServiceDataTypes.CvFrame},
                           "draw_landmarks": ServiceDataTypes.Boolean}
        self.output_type = {"face_landmarks": ServiceDataTypes.NumpyArray,
                            "annotated_image": ServiceDataTypes.CvFrame}
        self.num_faces = 10
        base_options = python.BaseOptions(
            model_asset_path=os.path.dirname(os.path.realpath(__file__)) + "/assets/face_landmarker.task")
        self.options = vision.FaceLandmarkerOptions(base_options=base_options,
                                                    output_face_blendshapes=True,
                                                    output_facial_transformation_matrixes=True,
                                                    num_faces=self.num_faces)
        self.detector = None

    def activate(self):
        self.detector = vision.FaceLandmarker.create_from_options(self.options)
        log("FaceLandmarks: <p style='color:blue'>Activated</p>")

    def configure(self, params):
        pass

    def process(self, input_data=None):
        numpy_image = input_data["camera_input"]["frame"]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)
        detection_result = self.detector.detect(image)
        draw_landmarks = self.context.get_state(
            "draw_landmarks", input_data["draw_landmarks"])
        annotated_image, face_landmarks = process_result(
            numpy_image, detection_result, draw_landmarks=draw_landmarks)
        return {"face_landmarks": face_landmarks, "annotated_image": annotated_image}

    def deactivate(self):
        self.detector = None
        log("FaceLandmarks: <p style='color:blue'>Deactivated</p>")
