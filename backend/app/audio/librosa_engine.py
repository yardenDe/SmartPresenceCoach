import librosa
import numpy as np

from media.config import SAMPLE_RATE


class LibrosaEngine:
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate

    def rms(self, audio: np.ndarray) -> np.ndarray:
        return librosa.feature.rms(y=audio)[0]

    def pitch(self, audio: np.ndarray) -> np.ndarray:
        return librosa.yin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=self.sample_rate,
        )
