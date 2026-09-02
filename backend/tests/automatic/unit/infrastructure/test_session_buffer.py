"""Tests for the in-memory session buffer."""


def test_add_flush_and_close():
    from infrastructure.session_buffer import SessionBuffer

    buffer = SessionBuffer(flush_size=2)
    assert buffer.add(10, {"overall": 80, "timestamp": 0.0}) is None

    flushed = buffer.add(10, {"overall": 90, "timestamp": 3.0})
    assert flushed == [
        {"overall": 80, "timestamp": 0.0},
        {"overall": 90, "timestamp": 3.0},
    ]
    assert buffer.get(10) == []

    buffer.add(10, {"overall": 95, "timestamp": 6.0})
    assert len(buffer.close_session(10)) == 1
    assert 10 not in buffer.buffers
