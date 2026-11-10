import numpy as np

from extraction.audio.librosa_engine import LibrosaEngine
from extraction.audio.transcriber import Transcriber
from extraction.video.landmarks_extractor import LandmarksExtractor
from extraction.audio.config import AudioFeatures


class ExtractionManager:
    def __init__(
        self,
        video_extractor: LandmarksExtractor,
        audio_engine: LibrosaEngine,
        transcriber: Transcriber | None = None,
    ):
        self.video_extractor = video_extractor
        self.audio_engine = audio_engine
        self.transcriber = transcriber

    def extract_video(self, frames: list[np.ndarray]):
        return self.video_extractor.process(frames)

    def extract_audio(self, audio: np.ndarray) -> AudioFeatures:
        return self.audio_engine.extract_features(audio)

    def transcribe(self, audio: np.ndarray) -> str | None:
        if self.transcriber is None:
            return None
        return self.transcriber.transcribe(audio).text
