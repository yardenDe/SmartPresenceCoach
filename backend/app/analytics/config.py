ANALYSIS_METRICS = (
    "focus",
    "posture",
    "presence",
    "engagement",
    "composure",
)


class AnalyticsConfig:
    DEFAULT_SCORE: float = 100.0
    MIN_SCORE: float = 0.0
    MAX_SCORE: float = 100.0
