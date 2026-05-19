from typing import TypeVar

from pydantic import BaseModel

from core.exceptions import LLMUnavailableError
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
        system_instruction: str | None = None,
        response_mime_type: str = "application/json",
    ) -> T:
        try:
            response = self.manager.generate(
                prompt,
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
                response_json_schema=response_model.model_json_schema(),
            )
            return response_model.model_validate_json(response)
        except Exception:
            self.logger.exception("event=llm.generate_json.failed")
            raise LLMUnavailableError()
