from analytics.config import METRIC_DEFINITIONS
from analytics.math_utils import average_scores, normalize_metric
from analytics.config import AudioMetrics, Scores, VideoMetrics


class ScoreCalculator:
    def calculate(
        self,
        video: VideoMetrics | None = None,
        audio: AudioMetrics | None = None,
    ) -> Scores | None:
        normalized = self._normalize_metrics(video, audio)
        if all(value is None for value in normalized.values()):
            return None

        focus = average_scores(
            normalized.get("face_direction"),
            normalized.get("head_movement"),
        )
        engagement = average_scores(
            normalized.get("movement_amount"),
            normalized.get("hand_movement"),
            normalized.get("pitch_variation"),
            normalized.get("volume_variation"),
        )
        posture = normalized.get("shoulder_tilt")
        composure = average_scores(
            normalized.get("movement_variation"),
            normalized.get("head_movement"),
            normalized.get("pause_ratio"),
        )
        presence = average_scores(
            normalized.get("face_direction"),
            normalized.get("movement_amount"),
            normalized.get("hand_movement"),
            normalized.get("average_volume"),
        )
        overall = average_scores(focus, engagement, posture, composure, presence)

        return Scores(
            focus=focus,
            engagement=engagement,
            posture=posture,
            composure=composure,
            presence=presence,
            overall=overall,
        )

    @staticmethod
    def _normalize_metrics(
        video: VideoMetrics | None,
        audio: AudioMetrics | None,
    ) -> dict[str, float | None]:
        normalized = {}
        for name, definition in METRIC_DEFINITIONS.items():
            value = getattr(video, name, None)
            if value is None:
                value = getattr(audio, name, None)
            normalized[name] = normalize_metric(value, definition)
        return normalized
