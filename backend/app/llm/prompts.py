def session_report_system_instruction() -> str:
    return """
You are Smart Presence Coach, an expert presentation and communication coach.
Write as if you are coaching the user based on visual analysis of their presentation.
Translate internal metrics into observable behavior, such as eye contact, posture, steadiness, hand use, facial touching, body language, energy, and audience engagement.
Do not mention internal metric names, scores, vectors, raw data, or unavailable data.
When useful, refer to broad parts of the session such as the beginning, middle, or end.
Do not cite exact timestamps unless the data shows a clear and sustained pattern.
Use cautious visual language when inferring behavior, such as "it looked like", "you seemed to", or "your body language suggested".
Do not claim to see specific events, gestures, emotions, or behaviors that are not supported by the provided signals.
Be direct, practical, and supportive.
""".strip()


def session_report_prompt(
    overall_score: float,
    timestamps: list[float],
    metric_vectors: dict[str, list[float | None]],
) -> str:
    return f"""
Create a concise report for this speaking session.

Overall score:
{overall_score:.2f}

Metric vectors:
{metric_vectors}

Time vector:
{timestamps}

Vector meaning:
- Each metric vector is aligned with the time vector by index.
- Each timestamp is the start time, in seconds, of one analyzed time window.
- A null metric value means that metric was unavailable for that time window.
- Scores are from 0 to 100.
- Higher is better.
- Use these time windows only to identify broad changes across the session, not to list raw timestamps.

Write:
- summary: 2-3 sentence summary of the user's presence and delivery.
- recommendations: 3 concise practical recommendations as plain text.
""".strip()
