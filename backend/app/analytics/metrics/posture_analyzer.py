from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, axis_distance, clamp_score, points_exist


class PostureAnalyzer(BaseAnalyzer):
    SHOULDER_ALIGNMENT_SCALE = 400.0
    DEFAULT_SCORE = 100.0

    def _compute_frame_score(self, frame_data):
        pose_data = frame_data.get("pose")

        if not points_exist(pose_data, "left_shoulder", "right_shoulder"):
            return 0.0

        shoulder_gap = axis_distance(
            pose_data["left_shoulder"],
            pose_data["right_shoulder"],
            "y",
        )

        return clamp_score(self.DEFAULT_SCORE - (shoulder_gap * self.SHOULDER_ALIGNMENT_SCALE))

    def compute(self, window_data):
        frame_scores = [self._compute_frame_score(frame_data) for frame_data in window_data]
        return clamp_score(average(frame_scores))

    def analyze(self, data):
        if isinstance(data, list):
            return self.compute(data)
        return self.compute([data])
