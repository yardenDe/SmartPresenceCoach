import os
from typing import Any, Dict

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    HandLandmarker,
    HandLandmarkerOptions,
    PoseLandmarker,
    PoseLandmarkerOptions,
)

from core.config import get_settings
from core.logger import get_logger

logger = get_logger("app.vision.mediapipe")


class MediaPipeDetector:
    def __init__(self) -> None:
        settings = get_settings()

        self.base_path = settings.MEDIAPIPE_MODEL_PATH
        self.running_mode = settings.MEDIAPIPE_RUNNING_MODE

        self.face_model = settings.FACE_LANDMARKER_MODEL
        self.pose_model = settings.POSE_LANDMARKER_MODEL
        self.hand_model = settings.HAND_LANDMARKER_MODEL

        self.face_detector: FaceLandmarker | None = None
        self.pose_detector: PoseLandmarker | None = None
        self.hand_detector: HandLandmarker | None = None

        logger.info("event=mediapipe.detector.init")

    def _get_face_detector(self) -> FaceLandmarker:
        if self.face_detector is None:
            logger.info("event=mediapipe.face.load.start")

            try:
                options = FaceLandmarkerOptions(
                    base_options=python.BaseOptions(
                        model_asset_path=os.path.join(
                            self.base_path,
                            self.face_model,
                        )
                    ),
                    running_mode=self.running_mode,
                )
                self.face_detector = FaceLandmarker.create_from_options(options)
            except Exception:
                logger.exception("event=mediapipe.face.load.failed")
                raise

            logger.info("event=mediapipe.face.load.done")

        return self.face_detector

    def _get_pose_detector(self) -> PoseLandmarker:
        if self.pose_detector is None:
            logger.info("event=mediapipe.pose.load.start")

            try:
                options = PoseLandmarkerOptions(
                    base_options=python.BaseOptions(
                        model_asset_path=os.path.join(
                            self.base_path,
                            self.pose_model,
                        )
                    ),
                    running_mode=self.running_mode,
                )
                self.pose_detector = PoseLandmarker.create_from_options(options)
            except Exception:
                logger.exception("event=mediapipe.pose.load.failed")
                raise

            logger.info("event=mediapipe.pose.load.done")

        return self.pose_detector

    def _get_hand_detector(self) -> HandLandmarker:
        if self.hand_detector is None:
            logger.info("event=mediapipe.hands.load.start")

            try:
                options = HandLandmarkerOptions(
                    base_options=python.BaseOptions(
                        model_asset_path=os.path.join(
                            self.base_path,
                            self.hand_model,
                        )
                    ),
                    running_mode=self.running_mode,
                )
                self.hand_detector = HandLandmarker.create_from_options(options)
            except Exception:
                logger.exception("event=mediapipe.hands.load.failed")
                raise

            logger.info("event=mediapipe.hands.load.done")

        return self.hand_detector


    def detect(
        self,
        image: Any,
        face_mode: bool = False,
        hand_mode: bool = False,
        pose_mode: bool = False,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        if face_mode:
            result["face_landmarks"] = (
                self._get_face_detector().detect(mp_image)
            )

        if pose_mode:
            result["pose_landmarks"] = (
                self._get_pose_detector().detect(mp_image)
            )

        if hand_mode:
            result["hands_landmarks"] = (
                self._get_hand_detector().detect(mp_image)
            )

        return result

    def close(self) -> None:
        if self.face_detector is not None:
            self.face_detector.close()

        if self.pose_detector is not None:
            self.pose_detector.close()

        if self.hand_detector is not None:
            self.hand_detector.close()

        logger.info("event=mediapipe.detector.close")