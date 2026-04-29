from analytics.metrics.base_analyzer import BaseAnalyzer
from analytics.math_utils import average, clamp_score, point_distance, point_exists, variance


class ComposureAnalyzer(BaseAnalyzer):
    DEFAULT_SCORE = 100.0
    HAND_NEAR_FACE_LIMIT = 0.15
    HAND_NEAR_FACE_PENALTY = 20.0
    HEAD_MOVEMENT_VARIANCE_SCALE = 500.0

    def _compute_hand_penalty(self, frame_data):
        face_data = frame_data.get("face")
        hands = frame_data.get("hands", [])

        if not point_exists(face_data, "iris_center") or not hands:
            return 0.0

        face_center = face_data["iris_center"]
        penalty = 0.0

        for hand in hands:
            wrist = hand.get("wrist")
            if not wrist:
                continue

            face_hand_distance = point_distance(wrist, face_center)
            if face_hand_distance < self.HAND_NEAR_FACE_LIMIT:
                penalty += self.HAND_NEAR_FACE_PENALTY

        return penalty

    def _compute_head_stability_penalty(self, window_data):
        nose_positions_x = []
        nose_positions_y = []

        for frame_data in window_data:
            pose_data = frame_data.get("pose")
            if not point_exists(pose_data, "nose"):
                continue

            nose_positions_x.append(pose_data["nose"]["x"])
            nose_positions_y.append(pose_data["nose"]["y"])

        if len(nose_positions_x) < 2:
            return 0.0

        movement_variance = variance(nose_positions_x) + variance(nose_positions_y)
        return movement_variance * self.HEAD_MOVEMENT_VARIANCE_SCALE

    def compute(self, window_data):
        hand_penalties = [
            self._compute_hand_penalty(frame_data)
            for frame_data in window_data
        ]

        average_hand_penalty = average(hand_penalties)
        stability_penalty = self._compute_head_stability_penalty(window_data)

        final_score = self.DEFAULT_SCORE - average_hand_penalty - stability_penalty
        return clamp_score(final_score)

    def analyze(self, data):
        if isinstance(data, list):
            return self.compute(data)
        return self.compute([data])
