import librosa
import numpy as np

from media.config import SAMPLE_RATE
from extraction.audio.config import AUDIO_HOP_LENGTH
from extraction.audio.config import AudioFeatures


class LibrosaEngine:
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate

    def rms(self, audio: np.ndarray) -> np.ndarray:
        return librosa.feature.rms(y=audio, hop_length=AUDIO_HOP_LENGTH)[0]

    def pitch(self, audio: np.ndarray) -> np.ndarray:
        return librosa.yin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=self.sample_rate,
            hop_length=AUDIO_HOP_LENGTH,
        )

    def non_silent_intervals(self, audio: np.ndarray) -> np.ndarray:
        return librosa.effects.split(y=audio, hop_length=AUDIO_HOP_LENGTH)

    def extract_features(self, audio: np.ndarray) -> AudioFeatures:
        return AudioFeatures(
            rms=self.rms(audio),
            pitch=self.pitch(audio),
            non_silent_intervals=self.non_silent_intervals(audio),
            total_samples=int(audio.size),
            sample_rate=self.sample_rate,
            hop_length=AUDIO_HOP_LENGTH,
        )
