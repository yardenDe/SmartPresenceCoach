import numpy as np

from audio.librosa_engine import LibrosaEngine
from audio.transcriber import Transcriber
from core.logger import get_logger
from schemas.analysis import AudioFeatures


logger = get_logger("app.audio.pipeline")


class AudioPipeline:
    def __init__(
        self,
        engine: LibrosaEngine,
        transcriber: Transcriber | None,
    ):
        self.engine = engine
        self.transcriber = transcriber

        logger.debug(
            "event=audio.pipeline.init transcription_enabled=%s",
            self.transcriber is not None,
        )

    def process(
        self,
        audio: np.ndarray,
    ) -> AudioFeatures:

        features = self.engine.extract_features(audio)

        if self.transcriber is not None:
            transcription = self.transcriber.transcribe(audio)
            features.transcript = transcription.text

        logger.debug(
            "event=audio.chunk.done samples=%s transcription_enabled=%s has_transcript=%s",
            audio.size,
            self.transcriber is not None,
            bool(features.transcript),
        )

        return features
