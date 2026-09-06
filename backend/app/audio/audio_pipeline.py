import numpy as np

from audio.audio_processor import AudioProcessor
from audio.librosa_engine import LibrosaEngine
from audio.transcriber import Transcriber
from schemas.analysis import AudioFeatures


class AudioPipeline:
    def __init__(
        self,
        processor: AudioProcessor,
        engine: LibrosaEngine,
        transcriber: Transcriber | None,
    ):
        self.processor = processor
        self.engine = engine
        self.transcriber = transcriber

<<<<<<< Updated upstream
    def process(self) -> dict[str, object]:
        audio = self.processor.extract()
=======
    def process(
        self,
        audio: np.ndarray,
    ) -> AudioFeatures:

        features = self.engine.extract_features(audio)

        if self.transcriber is None:
            return features
>>>>>>> Stashed changes

        transcription = self.transcriber.transcribe(
            self.processor.to_wav_bytes(audio)
        )

        features.transcript = transcription.text

        return features
