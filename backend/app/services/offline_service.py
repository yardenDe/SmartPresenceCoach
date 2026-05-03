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
        self.logger = get_logger("app.offline_service")
        self.logger.info("Initializing OfflineService")

        self.video_input = video
        self.video_path = None

        self.vision_pipline = None
        self.analytics = analytics
        self.video_storage = video_storage
        self.detector = detector


    async def process(self) -> dict[str, Any]:

        self.logger.info("Saving temp video")
        self.video_path = await self.video_storage.save_temp(self.video_input)
        self.logger.info(f"Video saved to temp path: {self.video_path}")
        self.logger.info("Initializing VisionPipeline with video path")

        self.vision_pipline = VisionPipeline(self.detector)

        chunk_index = 0
        chunk_results = []

        try:
            for landmarks_list in self.vision_pipline.pipline(video_path=self.video_path):

                chunk_index += 1

                self.logger.info(
                    f"Processing chunk {chunk_index} | frames={len(landmarks_list)}"
                )

                analysis = {
                    metric_name: float(score)
                    for metric_name, score in self.analytics.run_full_analysis(landmarks_list).items()
                }

                result = {
                    "chunk_id": chunk_index,
                    "scores": analysis,
                }

            
                for metric, score in analysis.items():
                    self.logger.info(
                      f"[CHUNK {chunk_index}] metric={metric} score={score:.2f}"
                )
                

                chunk_results.append(result)

            self.logger.info("Offline processing completed")
            return chunk_results

        finally:
            self.close()

    
    def close(self) -> None:

        self.logger.info("Cleaning up OfflineService")

        if self.vision_pipline:
            self.vision_pipline.close()

        if self.video_path:
            self.video_storage.delete(self.video_path)

        self.logger.info("Cleanup finished")
