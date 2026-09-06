import librosa
import numpy as np

<<<<<<< Updated upstream
from audio.config import SAMPLE_RATE
=======
from media.config import SAMPLE_RATE
from schemas.analysis import AudioFeatures
>>>>>>> Stashed changes


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

    def non_silent_intervals(self, audio: np.ndarray) -> np.ndarray:
        return librosa.effects.split(y=audio)

    def extract_features(self, audio: np.ndarray) -> AudioFeatures:
        return AudioFeatures(
            rms=self.rms(audio),
            pitch=self.pitch(audio),
            non_silent_intervals=self.non_silent_intervals(audio),
            total_samples=int(audio.size),
        )
