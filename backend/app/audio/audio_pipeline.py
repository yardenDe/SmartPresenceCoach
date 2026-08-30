import numpy as np

from audio.audio_processor import AudioProcessor
from audio.librosa_engine import LibrosaEngine


class AudioPipeline:
    def __init__(
        self,
        processor: AudioProcessor,
        engine: LibrosaEngine,
    ):
        self.processor = processor
        self.engine = engine

    def process(self) -> dict[str, np.ndarray]:
        audio = self.processor.extract()

        return {
            "rms": self.engine.rms(audio),
            "pitch": self.engine.pitch(audio),
        }
