from sqlalchemy.orm import Session
from vision.detectors import MediaPipeDetector


class LiveService:
    def __init__(self, db: Session):
        self.db = db
        self.detector = MediaPipeDetector()

    def frame_to_metrics(self, frame):

        landmarks = self.detector.detect(frame,face_mode=True, hand_mode=True, pose_mode=True )

        