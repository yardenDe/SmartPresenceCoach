from time import perf_counter

import librosa
import numpy as np

from analytics.config import AudioMetrics
from extraction.audio.config import AudioFeatures
from core.logger import get_logger

logger = get_logger("app.analytics.audio")


class AudioAnalyticsManager:
    def analyze(
        self,
        features: AudioFeatures,
    ) -> AudioMetrics:
        valid_rms = features.rms[features.rms > 0]

        valid_pitch = features.pitch[
            ~np.isnan(features.pitch) & (features.pitch > 0)
        ]

        volume_db = valid_rms
        if valid_rms.size:
            logger.debug("event=librosa.amplitude_to_db.start frames=%s", valid_rms.size)
            started = perf_counter()
            volume_db = librosa.amplitude_to_db(
                valid_rms,
                ref=1.0,
                top_db=None,
            )
            logger.debug("event=librosa.amplitude_to_db.done elapsed_seconds=%.4f", perf_counter() - started)

        pitch_semitones = valid_pitch
        if valid_pitch.size:
            logger.debug("event=librosa.hz_to_midi.start frames=%s", valid_pitch.size)
            started = perf_counter()
            pitch_semitones = librosa.hz_to_midi(valid_pitch)
            logger.debug("event=librosa.hz_to_midi.done elapsed_seconds=%.4f", perf_counter() - started)

        return AudioMetrics(
            pause_ratio=self._calculate_pause_ratio(
                features.non_silent_intervals,
                features.total_samples,
            ),
            average_volume=self._calculate_average_volume(
                volume_db
            ),
            volume_variation=self._calculate_volume_variation(
                volume_db
            ),
            pitch_variation=self._calculate_pitch_variation(
                pitch_semitones
            ),
        )

    def _calculate_average_volume(
        self,
        volume_db: np.ndarray,
    ) -> float | None:
        if volume_db.size == 0:
            return None

        return float(np.mean(volume_db))

    def _calculate_volume_variation(
        self,
        volume_db: np.ndarray,
    ) -> float | None:
        if volume_db.size == 0:
            return None

        return float(np.std(volume_db))

    def _calculate_pitch_variation(
        self,
        pitch_semitones: np.ndarray,
    ) -> float | None:
        if pitch_semitones.size == 0:
            return None

        return float(np.std(pitch_semitones))

    def _calculate_pause_ratio(
        self,
        non_silent_intervals: np.ndarray,
        total_samples: int,
    ) -> float | None:
        if total_samples == 0:
            return None

        non_silent_samples = sum(
            end - start
            for start, end in non_silent_intervals
        )

        return float(
            1 - (non_silent_samples / total_samples)
        )
