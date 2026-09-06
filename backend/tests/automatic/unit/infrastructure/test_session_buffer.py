"""Tests for the in-memory session buffer."""


def test_add_flush_and_close():
    from infrastructure.session_buffer import SessionBuffer
    from schemas.analysis import Analysis, VisualAnalysis

    buffer = SessionBuffer(flush_size=2)
    first = Analysis(visual=VisualAnalysis(overall=80))
    second = Analysis(visual=VisualAnalysis(overall=90))
    third = Analysis(visual=VisualAnalysis(overall=95))
    assert buffer.add(10, 0.0, first) is None

    flushed = buffer.add(10, 3.0, second)
    assert flushed == [
        {"timestamp": 0.0, "analysis": first},
        {"timestamp": 3.0, "analysis": second},
    ]
    assert buffer.get(10) == []

    buffer.add(10, 6.0, third)
    assert len(buffer.close_session(10)) == 1
    assert 10 not in buffer.buffers
