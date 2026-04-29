from vision.config import (
    MEDIAPIPE_POSE_MAP, 
    MEDIAPIPE_FACE_MAP, 
    MEDIAPIPE_HAND_MAP
)

class LandmarkManager:

    def filter_landmarks(self, landmarks_results: dict) -> dict:
        return {
            "pose": self._extract_pose(landmarks_results.get("pose_landmarks")),
            "face": self._extract_face(landmarks_results.get("face_landmarks")),
            "hands": self._extract_hands(landmarks_results.get("hands_landmarks")),
        }

    def _extract_pose(self, pose_data):
        if not pose_data or not getattr(pose_data, "pose_landmarks", None):
            return None
        
        pose_points = pose_data.pose_landmarks[0]
        extracted = {}
        
        for idx, name in MEDIAPIPE_POSE_MAP.items():
            if idx < len(pose_points):
                extracted[name] = {
                    "x": pose_points[idx].x,
                    "y": pose_points[idx].y
                }
        return extracted

    def _extract_face(self, face_data):
        if not face_data or not getattr(face_data, "face_landmarks", None):
            return None
        
        face_points = face_data.face_landmarks[0]
        extracted = {}
        
        for idx, name in MEDIAPIPE_FACE_MAP.items():
            if idx < len(face_points):
                extracted[name] = {
                    "x": face_points[idx].x,
                    "y": face_points[idx].y
                }
        return extracted

    def _extract_hands(self, hands_data):
        if not hands_data or not getattr(hands_data, "hand_landmarks", None):
            return []
        
        extracted_hands = []
        handedness_list = getattr(hands_data, "handedness", [])

        for hand_index, hand_points in enumerate(hands_data.hand_landmarks):
            if hand_index >= len(handedness_list) or len(hand_points) <= 8:
                continue

            hand_label = handedness_list[hand_index][0].category_name
            extracted_hand_points = {}

            for idx, name in MEDIAPIPE_HAND_MAP.items():
                if idx < len(hand_points):
                    extracted_hand_points[name] = {
                        "x": hand_points[idx].x,
                        "y": hand_points[idx].y
                    }

            extracted_hands.append({
                "label": hand_label,
                "points": extracted_hand_points
            })
            
        return extracted_hands