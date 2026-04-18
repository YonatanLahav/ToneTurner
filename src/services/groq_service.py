import json
import re
from typing import Optional

_CODE_FENCE_RE = re.compile(r'```(?:json)?\s*([\s\S]*?)```', re.IGNORECASE)

from groq import Groq

from src.config.settings import settings
from src.models.rephrase import RephraseRequest, RephraseResult
from src.services.base_llm import BaseLLM
from src.services.prompt_builder import PromptBuilder

_HEBREW_RE = re.compile(r'[\u0590-\u05FF]')


def _is_hebrew(text: str) -> bool:
    return bool(_HEBREW_RE.search(text))


class GroqService(BaseLLM):
    """Groq implementation of BaseLLM."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.groq_api_key
        if not key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY in environment or Streamlit secrets."
            )
        self._client = Groq(api_key=key)
        self._prompt_builder = PromptBuilder()

    def rephrase(self, request: RephraseRequest) -> RephraseResult:
        is_hebrew = _is_hebrew(request.text)
        messages = self._prompt_builder.build(request, is_hebrew)

        response = self._client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            response_format={"type": "json_object"},
        )

        if not response.choices:
            raise ValueError("Groq returned an empty response (no choices). The input may have been blocked by a safety filter.")

        raw = response.choices[0].message.content.strip()
        data = self._parse(raw)

        return RephraseResult.from_dict(
            data,
            source_language="hebrew" if is_hebrew else "english",
        )

    def _parse(self, raw: str) -> dict:
        # Extract content from code fence if present
        match = _CODE_FENCE_RE.search(raw)
        if match:
            raw = match.group(1).strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {raw}")

        missing = set(settings.default_tones) - data.keys()
        if missing:
            raise ValueError(f"Missing keys in API response: {missing}")

        return data
