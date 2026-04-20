import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    HandLandmarker,
    HandLandmarkerOptions,
    PoseLandmarker,
    PoseLandmarkerOptions
)

from core.config import get_settings

class MediaPipeDetector:
    def __init__(self):
        settings = get_settings()
        self.base_path = settings.MEDIAPIPE_MODEL_PATH
        self.running_mode = settings.MEDIAPIPE_RUNNING_MODE

        self.face_options = FaceLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=os.path.join(self.base_path, settings.FACE_LANDMARKER_MODEL)
            ),
            running_mode=self.running_mode,
        )
        
        self.pose_options = PoseLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=os.path.join(self.base_path, settings.POSE_LANDMARKER_MODEL)
            ),
            running_mode=self.running_mode,
        )

        self.hand_options = HandLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=os.path.join(self.base_path, settings.HAND_LANDMARKER_MODEL)
            ),
            running_mode=self.running_mode,
        )

        self.face_detector = FaceLandmarker.create_from_options(self.face_options)
        self.pose_detector = PoseLandmarker.create_from_options(self.pose_options)
        self.hand_detector = HandLandmarker.create_from_options(self.hand_options)


    def _detect_face(self, mp_image):
        return self.face_detector.detect(mp_image)

    def _detect_pose(self, mp_image):
        return self.pose_detector.detect(mp_image)

    def _detect_hands(self, mp_image):
        return self.hand_detector.detect(mp_image)

    def detect(self, mp_image, face_mode=False, hand_mode=False, pose_mode=False) -> dict:
        result = {}

        if face_mode:
            result['face'] = self._detect_face(mp_image)

        if pose_mode:
            result['pose'] = self._detect_pose(mp_image)

        if hand_mode:
            result['hands'] = self._detect_hands(mp_image)

        return result

    def close(self):
        self.face_detector.close()
        self.pose_detector.close()
        self.hand_detector.close()
