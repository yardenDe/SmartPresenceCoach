from typing import Any

from fastapi import UploadFile

from analytics.manager import AnalyticsManager
from vision.pipline import VisionPipeline
from vision.video_storage import VideoStorage
from vision.mediapipe_detector import MediaPipeDetector
from core.logger import get_logger


class OfflineService:

    def __init__(
        self,
        video: UploadFile,
        analytics: AnalyticsManager,
        video_storage: VideoStorage,
        detector: MediaPipeDetector,
    ):
        self.logger = get_logger("app.services.offline")

        self.video_input = video
        self.video_path = None

        self.vision_pipline = None
        self.analytics = analytics
        self.video_storage = video_storage
        self.detector = detector


    async def process(self) -> dict[str, Any]:

        self.logger.info("event=offline.process.start file=%s", self.video_input.filename)
        self.video_path = await self.video_storage.save_temp(self.video_input)

        self.vision_pipline = VisionPipeline(self.detector)

        chunk_index = 0
        chunk_results = []

        try:
            for landmarks_list in self.vision_pipline.pipline(video_path=self.video_path):

                chunk_index += 1

                analysis = {
                    metric_name: float(score)
                    for metric_name, score in self.analytics.run_full_analysis(landmarks_list).items()
                }

                result = {
                    "chunk_id": chunk_index,
                    "scores": analysis,
                }

                self.logger.info(
                    "event=offline.chunk.done chunk=%s frames=%s overall=%.2f",
                    chunk_index,
                    len(landmarks_list),
                    analysis.get("overall", 0.0),
                )

                chunk_results.append(result)

            self.logger.info("event=offline.process.done chunks=%s", len(chunk_results))
            return chunk_results

        finally:
            self.close()

    
    def close(self) -> None:
        if self.vision_pipline:
            self.vision_pipline.close()
            self.vision_pipline = None

        if self.video_path:
            self.video_storage.delete(self.video_path)
            self.video_path = None
