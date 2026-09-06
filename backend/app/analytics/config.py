<<<<<<< Updated upstream
=======
VISUAL_METRICS = (
    "focus",
    "posture",
    "presence",
    "engagement",
    "composure",
)

AUDIO_METRICS = (
    "pause_ratio",
    "average_volume",
    "volume_variation",
    "pitch_variation",
)


>>>>>>> Stashed changes
class AnalyticsConfig:
    DEFAULT_SCORE: float = 100.0
    MIN_SCORE: float = 0.0
    MAX_SCORE: float = 100.0
