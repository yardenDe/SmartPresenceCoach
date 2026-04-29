from enum import Enum

class AnalysisLevel(Enum):
    LEVEL1 = 1
    LEVEL2 = 2

class PointNames:
    NOSE = "nose"
    LEFT_EYE_BASIC = "left_eye_basic"
    RIGHT_EYE_BASIC = "right_eye_basic"
    LEFT_SHOULDER = "left_shoulder"
    RIGHT_SHOULDER = "right_shoulder"
    LEFT_ELBOW = "left_elbow"
    RIGHT_ELBOW = "right_elbow"
    LEFT_WRIST_BASIC = "left_wrist_basic"
    RIGHT_WRIST_BASIC = "right_wrist_basic"
    LEFT_HIP = "left_hip"
    RIGHT_HIP = "right_hip"
    LEFT_KNEE = "left_knee"
    RIGHT_KNEE = "right_knee"
    LEFT_ANKLE = "left_ankle"
    RIGHT_ANKLE = "right_ankle"

    IRIS_CENTER = "iris_center"
    MOUTH_TOP = "mouth_top"
    MOUTH_BOTTOM = "mouth_bottom"
    LEFT_EYEBROW = "left_eyebrow"
    RIGHT_EYEBROW = "right_eyebrow"
    CHIN = "chin"

    HAND_WRIST = "hand_wrist"
    HAND_INDEX_TIP = "hand_index_tip"
    HAND_THUMB_TIP = "hand_thumb_tip"

MEDIAPIPE_POSE_MAP = {
    0: PointNames.NOSE,
    1: PointNames.LEFT_EYE_BASIC,
    4: PointNames.RIGHT_EYE_BASIC,
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

MEDIAPIPE_FACE_MAP = {
    468: PointNames.IRIS_CENTER,
    13: PointNames.MOUTH_TOP,
    14: PointNames.MOUTH_BOTTOM,
    70: PointNames.LEFT_EYEBROW,
    300: PointNames.RIGHT_EYEBROW,
    152: PointNames.CHIN
}

MEDIAPIPE_HAND_MAP = {
    0: PointNames.HAND_WRIST,
    4: PointNames.HAND_THUMB_TIP,
    8: PointNames.HAND_INDEX_TIP
}