import os
from typing import Dict, Any
import cv2
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


    def _detect_face(self, mp_image: Any) -> Any:
        return self.face_detector.detect(mp_image)

    def _detect_pose(self, mp_image: Any) -> Any:
        return self.pose_detector.detect(mp_image)

    def _detect_hands(self, mp_image: Any) -> Any:
        return self.hand_detector.detect(mp_image)

    def detect(
        self,
        image: Any,
        face_mode: bool = False,
        hand_mode: bool = False,
        pose_mode: bool = False,
    ) -> Dict[str, Any]:
        result = {}

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        if face_mode:
            result['face_landmarks'] = self._detect_face(mp_image)

        if pose_mode:
            result['pose_landmarks'] = self._detect_pose(mp_image)

        if hand_mode:
            result['hands_landmarks'] = self._detect_hands(mp_image)

        return result

    def close(self) -> None:
        self.face_detector.close()
        self.pose_detector.close()
        self.hand_detector.close()
