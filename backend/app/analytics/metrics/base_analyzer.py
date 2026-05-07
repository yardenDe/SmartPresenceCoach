from abc import ABC, abstractmethod
from typing import Any


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        pass
