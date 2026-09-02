"""In-memory buffering for analysis snapshots awaiting persistence."""

from typing import Any

from core.logger import get_logger

logger = get_logger("app.infrastructure.session_buffer")


class SessionBuffer:
    def __init__(self, flush_size: int = 2):
        self.buffers: dict[int, list[dict[str, Any]]] = {}
        self.flush_size = flush_size

    def add(self, session_id: int, snapshot: dict[str, Any]) -> list[dict[str, Any]] | None:
        if session_id not in self.buffers:
            self.buffers[session_id] = []
            logger.debug("event=session_buffer.create session_id=%s", session_id)

        self.buffers[session_id].append(snapshot)

        logger.debug(
            "event=session_buffer.add session_id=%s size=%s",
            session_id,
            len(self.buffers[session_id]),
        )

        if len(self.buffers[session_id]) >= self.flush_size:
            return self.flush(session_id)
        return None

    def get(self, session_id: int) -> list[dict[str, Any]]:
        return self.buffers.get(session_id, [])


    def flush(self, session_id: int) -> list[dict[str, Any]] | None:
        buffer = self.buffers.get(session_id, [])

        if not buffer:
            logger.debug("event=session_buffer.flush.empty session_id=%s", session_id)
            return None

        self.buffers[session_id] = []

        logger.info(
            "event=session_buffer.flush.done session_id=%s count=%s",
            session_id,
            len(buffer),
        )

        return buffer

    def close_session(self, session_id: int) -> list[dict[str, Any]] | None:
        buffer = self.flush(session_id)

        if session_id in self.buffers:
            del self.buffers[session_id]

        logger.debug("event=session_buffer.session.closed session_id=%s", session_id)

        return buffer
