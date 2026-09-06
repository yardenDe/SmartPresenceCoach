import numpy as np

from audio.librosa_engine import LibrosaEngine
from audio.transcriber import Transcriber
from schemas.analysis import AudioFeatures


class AudioPipeline:
    def __init__(
        self,
        engine: LibrosaEngine,
        transcriber: Transcriber | None,
    ):
        self.engine = engine
        self.transcriber = transcriber

    def process(
        self,
        audio: np.ndarray,
    ) -> AudioFeatures:

        features = self.engine.extract_features(audio)

        if self.transcriber is None:
            return features

        transcription = self.transcriber.transcribe(audio)

        features.transcript = transcription.text

        return features
