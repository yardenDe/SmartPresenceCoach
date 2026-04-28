from typing import Any

from sqlalchemy.orm import Session

from vision.landmark_extractor import extract_relevant_landmarks
from analytics.manager import AnalyticsManager
from vision.detectors import MediaPipeDetector


class LiveService:
    def __init__(self, db: Session):
        self.db = db
        self.detector = MediaPipeDetector()
        self.analytics_manager = AnalyticsManager()

    def process_frame(self, frame: Any, session_id: int):
        raw_results = self.detector.detect(frame, face_mode=True, hand_mode=True, pose_mode=True)

        if not raw_results:
            return None

        relevant_data = extract_relevant_landmarks(raw_results)
        analysis_scores = self.analytics_manager.run_full_analysis(relevant_data)

        return {
            "session_id": session_id,
            "landmarks": relevant_data,
            "scores": analysis_scores,
        }
