import numpy as np

from schemas.analysis import AudioAnalysis, AudioFeatures


class AudioAnalyticsManager:
    def analyze(
        self,
        features: AudioFeatures,
    ) -> AudioAnalysis:
        valid_pitch = features.pitch[
            ~np.isnan(features.pitch)
        ]

        return AudioAnalysis(
            transcript=features.transcript,
            pause_ratio=self._calculate_pause_ratio(
                features.non_silent_intervals,
                features.total_samples,
            ),
            average_volume=self._calculate_average_volume(
                features.rms
            ),
            volume_variation=self._calculate_volume_variation(
                features.rms
            ),
            pitch_variation=self._calculate_pitch_variation(
                valid_pitch
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
