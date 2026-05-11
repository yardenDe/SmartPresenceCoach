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

    def generate(self, prompt: str) -> str:
        logger.debug("event=llm.generate.start model=%s", self.model)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            ),
        )

        text = response.text or ""
        logger.debug("event=llm.generate.done chars=%s", len(text))
        return text.strip()
