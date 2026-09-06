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
        volume_db = 20 * np.log10(valid_rms) if valid_rms.size else valid_rms
        pitch_semitones = (
            12 * np.log2(valid_pitch / 440.0)
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
        rms: np.ndarray,
    ) -> float | None:
        if rms.size == 0:
            return None

        return float(np.mean(rms))

    def _calculate_volume_variation(
        self,
        rms: np.ndarray,
    ) -> float | None:
        if rms.size == 0:
            return None

        return float(np.std(rms))

    def _calculate_pitch_variation(
        self,
        pitch: np.ndarray,
    ) -> float | None:
        if pitch.size == 0:
            return None

        return float(np.std(pitch))

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
