from typing import Dict, List, Any

from core.logger import get_logger

logger = get_logger("app.db.buffer_manager")


class BufferManager:
    def __init__(self, flush_size: int = 2):
        self.buffers: Dict[int, List[dict[str, Any]]] = {}
        self.flush_size = flush_size

    def add(self, session_id: int, snapshot: dict[str, Any]) -> None:
        if session_id not in self.buffers:
            self.buffers[session_id] = []
            logger.debug("event=buffer.create session_id=%s", session_id)

        self.buffers[session_id].append(snapshot)

        logger.debug(
            "event=buffer.add session_id=%s size=%s",
            session_id,
            len(self.buffers[session_id]),
        )

        return None

    def get(self, session_id: int) -> List[dict[str, Any]]:
        return self.buffers.get(session_id, [])

    def should_flush(self, session_id: int) -> bool:
        buffer = self.buffers.get(session_id, [])

        if not buffer:
            return False

        should_flush = len(buffer) >= self.flush_size

        if should_flush:
            logger.info(
                "event=buffer.should_flush.true session_id=%s count=%s flush_size=%s",
                session_id,
                len(buffer),
                self.flush_size,
            )

        return should_flush

    def flush(self, session_id: int) -> List[dict[str, Any]]:
        buffer = self.buffers.get(session_id, [])

        if not buffer:
            logger.debug("event=buffer.flush.empty session_id=%s", session_id)
            return []

        self.buffers[session_id] = []

        logger.info(
            "event=buffer.flush.done session_id=%s count=%s",
            session_id,
            len(buffer),
        )

        return buffer

    def close_session(self, session_id: int) -> List[dict[str, Any]]:
        buffer = self.flush(session_id)

        if session_id in self.buffers:
            del self.buffers[session_id]

        logger.debug("event=buffer.session.closed session_id=%s", session_id)

        return buffer
