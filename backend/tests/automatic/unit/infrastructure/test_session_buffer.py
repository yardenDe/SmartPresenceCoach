"""Tests for buffering complete snapshots without mixing sessions."""

from infrastructure.session_buffer import SessionBuffer
from models.snapshot import Snapshot


def test_buffer_flushes_complete_snapshots_and_closes_session():
    buffer = SessionBuffer(flush_size=2)
    first = Snapshot(session_id=10, timestamp=0.0, gaze_direction=2.0)
    second = Snapshot(session_id=10, timestamp=3.0, gaze_direction=4.0)
    other = Snapshot(session_id=20, timestamp=0.0, average_volume=-20.0)

    assert buffer.add(first) is None
    assert buffer.add(other) is None
    assert buffer.add(second) == [first, second]
    assert buffer.buffers[10] == []
    assert buffer.close_session(20) == [other]
    assert 20 not in buffer.buffers
    assert buffer.close_session(10) is None
    assert buffer.close_session(999) is None
