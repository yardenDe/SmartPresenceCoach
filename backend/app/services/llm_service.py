import json
from typing import TypeVar

from pydantic import BaseModel

from core.logger import get_logger
from llm.manager import Manager

T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.logger = get_logger("app.llm.service")

    def generate_json(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        response = self.manager.generate(prompt)
        data = json.loads(self._clean_json_response(response))

        if not isinstance(data, dict):
            raise ValueError("LLM response must be a JSON object")

        return response_model.model_validate(data)

    def _clean_json_response(self, response: str) -> str:
        text = response.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json").strip()
        elif text.startswith("```"):
            text = text.removeprefix("```").strip()

        if text.endswith("```"):
            text = text.removesuffix("```").strip()

        return text
