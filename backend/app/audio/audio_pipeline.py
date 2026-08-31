import numpy as np

from audio.librosa_engine import LibrosaEngine
from audio.transcriber import Transcriber


class AudioPipeline:
    def __init__(
        self,
        engine: LibrosaEngine,
        transcriber: Transcriber,
    ):
        self.engine = engine
        self.transcriber = transcriber

    def process(
        self,
        audio: np.ndarray,
    ) -> dict[str, object]:

        transcription = self.transcriber.transcribe(audio)

        return {
            "rms": self.engine.rms(audio),
            "pitch": self.engine.pitch(audio),
            "text": transcription.text,
            "words": transcription.words,
            "segments": transcription.segments,
        }