from google import genai
from google.genai import types

from core.logger import get_logger

logger = get_logger("app.llm.manager")


class Manager:
    def __init__(
        self,
        client: genai.Client,
        model: str,
        temperature: float,
        max_output_tokens: int,
    ):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_mime_type: str | None = "application/json",
        response_json_schema: dict | None = None,
    ) -> str:
        logger.debug("event=llm.generate.start model=%s", self.model)

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            system_instruction=system_instruction,
            response_mime_type=response_mime_type,
            response_json_schema=response_json_schema,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        text = response.text or ""
        logger.debug("event=llm.generate.done chars=%s", len(text))
        return text.strip()
