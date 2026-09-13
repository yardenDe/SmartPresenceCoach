import librosa
import numpy as np

from schemas.analysis import AudioFeatures, AudioMetrics


class AudioAnalyticsManager:
    def analyze(
        self,
        features: AudioFeatures,
    ) -> AudioMetrics:
        valid_rms = features.rms[features.rms > 0]

        valid_pitch = features.pitch[
            ~np.isnan(features.pitch) & (features.pitch > 0)
        ]

        volume_db = (
            librosa.amplitude_to_db(
                valid_rms,
                ref=1.0,
                top_db=None,
            )
            if valid_rms.size
            else valid_rms
        )

        pitch_semitones = (
            librosa.hz_to_midi(valid_pitch)
            if valid_pitch.size
            else valid_pitch
        )

        return AudioMetrics(
            transcript=features.transcript,
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