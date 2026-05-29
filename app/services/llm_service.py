from functools import lru_cache

from openai import OpenAI

from app.config import get_settings


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    s = get_settings()
    # Ollama exposes an OpenAI-compatible chat API at /v1; the SDK works as-is.
    return OpenAI(
        api_key=s.active_llm_key,
        base_url=s.active_llm_base_url,
        max_retries=5,
        timeout=300.0,
    )


class OpenAIClient:
    """Thin wrapper around the OpenAI-compatible chat completion endpoint.

    Backed by a local Ollama daemon. Class name is retained because the
    underlying SDK is the OpenAI Python client speaking to an OpenAI-shaped API.
    """

    @staticmethod
    def complete(prompt: str, json_mode: bool = False, temperature: float = 0.2) -> str:
        s = get_settings()
        kwargs: dict = {
            "model": s.active_llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = _client().chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
