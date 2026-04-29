from analytics.manager import AnalyticsManager
from services.vision_service import VisionService


class OfflineService:
    def __init__(self, video_path, chunk_sec=180):
        self.video_path = video_path
        self.chunk_sec = chunk_sec
        self.vision_service = VisionService(video_path=self.video_path, level="offline")
        self.analytics = AnalyticsManager()

    def iter_chunk_results(self):
        for chunk_index, chunk_frames in enumerate(
            self.vision_service.extract_video_chunks(chunk_sec=self.chunk_sec)
        ):
            landmarks = self.vision_service.process_video_chunk(chunk_frames)
            analysis = self.analytics.run_full_analysis(landmarks)

            yield {
                "chunk_index": chunk_index,
                "landmarks": landmarks,
                "analysis": analysis,
            }

    def service(self):
        return self.iter_chunk_results()

    def close(self):
        self.vision_service.close()
