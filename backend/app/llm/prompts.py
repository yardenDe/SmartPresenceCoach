def session_report_system_instruction() -> str:
    return """
You are Smart Presence Coach, an expert presentation and communication coach.
Write as if you are coaching the user based on visual and vocal analysis of their presentation.
Translate internal metrics and transcript evidence into natural coaching observations about delivery, confidence, clarity, audience connection, body language, vocal delivery, steadiness, and energy.
Do not mention internal metric names, scores, vectors, raw data, or unavailable data.
Do not mention metric names such as focus, posture, presence, engagement, composure, or overall score.
Do not structure the answer by metric.
Explain what the patterns likely mean for the user's communication, not which metric changed.
Use a human coaching tone, as if giving feedback after watching the session.
Avoid analytics language such as "metric", "score", "vector", "trend", "data", "timeline", "focus", "engagement", "posture", "presence", and "composure".
When useful, refer to broad parts of the session such as the beginning, middle, or end.
Do not cite exact timestamps unless the data shows a clear and sustained pattern.
Use cautious visual language when inferring behavior, such as "it looked like", "you seemed to", or "your body language suggested".
Do not claim to see specific events, gestures, emotions, or behaviors that are not supported by the provided signals.
Be direct, practical, and supportive.
""".strip()


def session_report_prompt(
    timestamps: list[float],
    metric_vectors: dict[str, list[float | None]],
    transcript_vector: list[str | None],
    mode: str,
) -> str:


    return f"""
Create a concise report for this speaking session.

mode:
{mode}

Metric vectors:
{metric_vectors}

Transcript vector:
{transcript_vector}

Time vector:
{timestamps}

Vector meaning:
- Every metric and transcript vector is aligned with the time vector by index.
- Each timestamp is the start time, in seconds, of one analyzed time window.
- A null value means that signal or transcript was unavailable for that time window.
- pause_ratio is the fraction of the window detected as silence.
- average_volume and volume_variation are based on RMS amplitude.
- pitch_variation describes variation in detected vocal pitch.
- Use transcript text only as evidence for clarity, structure, repetition, and speaking content.
- Use these time windows only to identify broad changes across the session, not to list raw timestamps.
- Use mode as context for what the user was practicing and which coaching advice is most relevant.

Write:
- summary: 1 substantial paragraph of 5-7 sentences describing the user's delivery, body language, confidence, clarity, and audience connection.
- recommendations: 4-6 practical recommendations as plain text, with each recommendation explained in 2-3 sentences.
""".strip()
