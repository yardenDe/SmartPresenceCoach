from enum import Enum

class AnalysisLevel(Enum):
    LEVEL1 = 1
    LEVEL2 = 2

CHUNK_SECONDS = 3
TARGET_FPS = 3

class PointNames:
    NOSE: str = "nose"
    LEFT_EYE_BASIC: str = "left_eye_basic"
    RIGHT_EYE_BASIC: str = "right_eye_basic"
    LEFT_EAR: str = "left_ear"
    RIGHT_EAR: str = "right_ear"
    LEFT_SHOULDER: str = "left_shoulder"
    RIGHT_SHOULDER: str = "right_shoulder"
    LEFT_ELBOW: str = "left_elbow"
    RIGHT_ELBOW: str = "right_elbow"
    LEFT_WRIST_BASIC: str = "left_wrist_basic"
    RIGHT_WRIST_BASIC: str = "right_wrist_basic"
    LEFT_HIP: str = "left_hip"
    RIGHT_HIP: str = "right_hip"
    LEFT_KNEE: str = "left_knee"
    RIGHT_KNEE: str = "right_knee"
    LEFT_ANKLE: str = "left_ankle"
    RIGHT_ANKLE: str = "right_ankle"

    IRIS_CENTER: str = "iris_center"
    LEFT_IRIS_CENTER: str = "left_iris_center"
    RIGHT_IRIS_CENTER: str = "right_iris_center"
    LEFT_EYE_OUTER: str = "left_eye_outer"
    LEFT_EYE_INNER: str = "left_eye_inner"
    RIGHT_EYE_INNER: str = "right_eye_inner"
    RIGHT_EYE_OUTER: str = "right_eye_outer"
    MOUTH_TOP: str = "mouth_top"
    MOUTH_BOTTOM: str = "mouth_bottom"
    CHIN: str = "chin"
    FOREHEAD: str = "forehead"
    LEFT_CHEEK: str = "left_cheek"
    RIGHT_CHEEK: str = "right_cheek"

    HAND_WRIST: str = "hand_wrist"
    HAND_INDEX_TIP: str = "hand_index_tip"
    HAND_THUMB_TIP: str = "hand_thumb_tip"
    HAND_MIDDLE_TIP: str = "hand_middle_tip"
    HAND_RING_TIP: str = "hand_ring_tip"
    HAND_PINKY_TIP: str = "hand_pinky_tip"

MEDIAPIPE_POSE_MAP: dict[int, str] = {
    0: PointNames.NOSE,
    1: PointNames.LEFT_EYE_BASIC,
    4: PointNames.RIGHT_EYE_BASIC,
    7: PointNames.LEFT_EAR,
    8: PointNames.RIGHT_EAR,
    11: PointNames.LEFT_SHOULDER,
    12: PointNames.RIGHT_SHOULDER,
    13: PointNames.LEFT_ELBOW,
    14: PointNames.RIGHT_ELBOW,
    15: PointNames.LEFT_WRIST_BASIC,
    16: PointNames.RIGHT_WRIST_BASIC,
    23: PointNames.LEFT_HIP,
    24: PointNames.RIGHT_HIP,
    25: PointNames.LEFT_KNEE,
    26: PointNames.RIGHT_KNEE,
    27: PointNames.LEFT_ANKLE,
    28: PointNames.RIGHT_ANKLE
}

MEDIAPIPE_FACE_MAP: dict[int, str] = {
    468: PointNames.LEFT_IRIS_CENTER,
    473: PointNames.RIGHT_IRIS_CENTER,
    33: PointNames.LEFT_EYE_OUTER,
    133: PointNames.LEFT_EYE_INNER,
    362: PointNames.RIGHT_EYE_INNER,
    263: PointNames.RIGHT_EYE_OUTER,
    13: PointNames.MOUTH_TOP,
    14: PointNames.MOUTH_BOTTOM,
    152: PointNames.CHIN,
    10: PointNames.FOREHEAD,
    234: PointNames.LEFT_CHEEK,
    454: PointNames.RIGHT_CHEEK
}

MEDIAPIPE_HAND_MAP: dict[int, str] = {
    0: PointNames.HAND_WRIST,
    4: PointNames.HAND_THUMB_TIP,
    8: PointNames.HAND_INDEX_TIP,
    12: PointNames.HAND_MIDDLE_TIP,
    16: PointNames.HAND_RING_TIP,
    20: PointNames.HAND_PINKY_TIP
}
