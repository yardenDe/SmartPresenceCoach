from time import perf_counter

import librosa
import numpy as np

from media.config import SAMPLE_RATE
from extraction.audio.config import (
    AUDIO_HOP_LENGTH,
    WARMUP_AMPLITUDE,
    WARMUP_DURATION_SECONDS,
    WARMUP_FREQUENCY_HZ,
    AudioFeatures,
)
from core.logger import get_logger

logger = get_logger("app.extraction.audio.librosa")


class LibrosaEngine:
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate

    def warmup(self) -> None:
        logger.info("event=librosa.warmup.start")
        started = perf_counter()
        times = np.arange(round(self.sample_rate * WARMUP_DURATION_SECONDS)) / self.sample_rate
        audio = (WARMUP_AMPLITUDE * np.sin(2 * np.pi * WARMUP_FREQUENCY_HZ * times)).astype(np.float32)
        self.extract_features(audio)
        logger.info("event=librosa.warmup.done elapsed_seconds=%.4f", perf_counter() - started)

    def rms(self, audio: np.ndarray) -> np.ndarray:
        logger.debug("event=librosa.rms.start samples=%s", audio.size)
        started = perf_counter()
        result = librosa.feature.rms(y=audio, hop_length=AUDIO_HOP_LENGTH)[0]
        logger.debug("event=librosa.rms.done elapsed_seconds=%.4f frames=%s", perf_counter() - started, result.size)
        return result

    def pitch(self, audio: np.ndarray) -> np.ndarray:
        logger.debug("event=librosa.note_to_hz.start note=C2")
        started = perf_counter()
        fmin = librosa.note_to_hz("C2")
        logger.debug("event=librosa.note_to_hz.done note=C2 elapsed_seconds=%.4f", perf_counter() - started)
        logger.debug("event=librosa.note_to_hz.start note=C7")
        started = perf_counter()
        fmax = librosa.note_to_hz("C7")
        logger.debug("event=librosa.note_to_hz.done note=C7 elapsed_seconds=%.4f", perf_counter() - started)

        logger.debug("event=librosa.yin.start samples=%s sample_rate=%s", audio.size, self.sample_rate)
        started = perf_counter()
        result = librosa.yin(
            audio,
            fmin=fmin,
            fmax=fmax,
            sr=self.sample_rate,
            hop_length=AUDIO_HOP_LENGTH,
        )
        logger.debug("event=librosa.yin.done elapsed_seconds=%.4f frames=%s", perf_counter() - started, result.size)
        return result

    def non_silent_intervals(self, audio: np.ndarray) -> np.ndarray:
        logger.debug("event=librosa.split.start samples=%s", audio.size)
        started = perf_counter()
        result = librosa.effects.split(y=audio, hop_length=AUDIO_HOP_LENGTH)
        logger.debug("event=librosa.split.done elapsed_seconds=%.4f intervals=%s", perf_counter() - started, len(result))
        return result

    def extract_features(self, audio: np.ndarray) -> AudioFeatures:
        return AudioFeatures(
            rms=self.rms(audio),
            pitch=self.pitch(audio),
            non_silent_intervals=self.non_silent_intervals(audio),
            total_samples=int(audio.size),
            sample_rate=self.sample_rate,
            hop_length=AUDIO_HOP_LENGTH,
        )
