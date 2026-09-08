import os
from typing import Any

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import (
    PoseLandmarker,
    PoseLandmarkerOptions,
    PoseLandmarkerResult,
    RunningMode,
)

from core.logger import get_logger

logger = get_logger("app.vision.mediapipe")


class MediaPipeDetector:
    def __init__(
        self,
        model_path: str,
        model_name: str,
        running_mode: RunningMode,
    ) -> None:
        self.base_path = model_path
        self.running_mode = running_mode
        self.pose_model = model_name

        self.pose_detector: PoseLandmarker | None = None

        logger.info("event=mediapipe.detector.init")

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

    def detect(
        self,
        image: Any,
    ) -> PoseLandmarkerResult:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        return self._get_pose_detector().detect(mp_image)

    def close(self) -> None:
        if self.pose_detector is not None:
            self.pose_detector.close()

        logger.info("event=mediapipe.detector.close")
