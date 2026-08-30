import numpy as np

from audio.audio_processor import AudioProcessor
from audio.librosa_engine import LibrosaEngine
from audio.transcriber import Transcriber


class AudioPipeline:
    def __init__(
        self,
        processor: AudioProcessor,
        engine: LibrosaEngine,
        transcriber: Transcriber,
    ):
        self.processor = processor
        self.engine = engine
        self.transcriber = transcriber

    def process(self) -> dict[str, object]:
        audio = self.processor.extract()

        transcription = self.transcriber.transcribe(
            self.processor.to_wav_bytes(audio)
        )

        return {
            "rms": self.engine.rms(audio),
            "pitch": self.engine.pitch(audio),
            "text": transcription.text,
            "words": transcription.words,
            "segments": transcription.segments,
        }