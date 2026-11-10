from dataclasses import dataclass

import numpy as np


AUDIO_HOP_LENGTH = 512


@dataclass
class AudioFeatures:
    rms: np.ndarray
    pitch: np.ndarray
    non_silent_intervals: np.ndarray
    total_samples: int
    sample_rate: int
    hop_length: int

    def to_dict(self) -> dict:
        return {
            name: value.tolist() if isinstance(value, np.ndarray) else value
            for name, value in vars(self).items()
        }
