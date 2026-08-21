from google import genai
from google.genai.errors import ClientError

from core.config import get_settings


def test_llm_connection():
    settings = get_settings()

    assert settings.LLM_API_KEY, "LLM_API_KEY is missing"

    client = genai.Client(api_key=settings.LLM_API_KEY)

    try:
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents="Reply with exactly: OK",
        )
    except ClientError as exc:
        raise AssertionError(f"Gemini API request failed: {exc}") from exc

    assert response.text, "Gemini returned an empty response"

    print("\nLLM connection successful")
    print(f"Model: {settings.LLM_MODEL}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    test_llm_connection()