from analytics.config import METRIC_DEFINITIONS
from analytics.math_utils import average_scores, normalize_metric
from schemas.analysis import AudioMetrics, Scores, VisualMetrics


class ScoreCalculator:
    def calculate(
        self,
        visual: VisualMetrics | None,
        audio: AudioMetrics | None,
    ) -> Scores | None:
        if visual is None and audio is None:
            return None

        normalized = self._normalize_metrics(visual, audio)

        focus = average_scores(
            normalized.get("gaze_direction"),
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
            normalized.get("gaze_direction"),
            normalized.get("movement_amount"),
            normalized.get("hand_movement"),
            normalized.get("average_volume"),
        )

        overall = average_scores(
            focus,
            engagement,
            posture,
            composure,
            presence,
        )

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
        visual: VisualMetrics | None,
        audio: AudioMetrics | None,
    ) -> dict[str, float | None]:
        metrics = {}

        if visual is not None:
            metrics.update(visual.model_dump())

        if audio is not None:
            metrics.update(audio.model_dump(exclude={"transcript"}))

        return {
            metric_name: normalize_metric(
                metric_value,
                METRIC_DEFINITIONS[metric_name],
            )
            for metric_name, metric_value in metrics.items()
        }
