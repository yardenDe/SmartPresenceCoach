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

MEDIAPIPE_LANDMARKS: dict[int, str] = {
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
