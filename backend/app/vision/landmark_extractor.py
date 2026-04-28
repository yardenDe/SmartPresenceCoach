import time
from vision.config import POSE_LANDMARKS_MAP, FACE_LANDMARKS_MAP, DEFAULT_POSE_POINTS

def extract_relevant_landmarks(raw_results, extra_points=None):
    relevant_landmarks = {
        "timestamp": time.time(),
        "pose": None,
        "face": None,
        "hands": [],
    }

    pose_landmarks = raw_results.get("pose_landmarks")
    if pose_landmarks and getattr(pose_landmarks, "pose_landmarks", None):
        pose_points = pose_landmarks.pose_landmarks[0]
        relevant_landmarks["pose"] = {}
        
        points_to_extract = DEFAULT_POSE_POINTS + (extra_points or [])
        
        for point in points_to_extract:
            if point in POSE_LANDMARKS_MAP and point < len(pose_points):
                name = POSE_LANDMARKS_MAP[point]
                relevant_landmarks["pose"][name] = {
                    "x": pose_points[point].x,
                    "y": pose_points[point].y
                }

    face_landmarks = raw_results.get("face_landmarks")
    if face_landmarks and getattr(face_landmarks, "face_landmarks", None):
        face_points = face_landmarks.face_landmarks[0]
        relevant_landmarks["face"] = {}
        
        for point, name in FACE_LANDMARKS_MAP.items():
            if point < len(face_points):
                relevant_landmarks["face"][name] = {
                    "x": face_points[point].x,
                    "y": face_points[point].y
                }

    hands_landmarks = raw_results.get("hands_landmarks")
    if hands_landmarks and getattr(hands_landmarks, "hand_landmarks", None):
        handedness_list = getattr(hands_landmarks, "handedness", [])

        for hand_index, hand_points in enumerate(hands_landmarks.hand_landmarks):
            if hand_index >= len(handedness_list) or len(hand_points) <= 8:
                continue

            hand_label = handedness_list[hand_index][0].category_name

            relevant_landmarks["hands"].append({
                "label": hand_label,
                "wrist": {"x": hand_points[0].x, "y": hand_points[0].y},
                "index_tip": {"x": hand_points[8].x, "y": hand_points[8].y},
            })

    return relevant_landmarks