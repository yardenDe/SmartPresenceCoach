from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data: Dict[str, Any] | list[Dict[str, Any]]) -> float:
        pass
