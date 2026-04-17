import json
import re
from typing import Dict, Optional
from groq import Groq
from src.config.settings import settings


def detect_hebrew(text: str) -> bool:
    """Detect if text contains Hebrew characters.

    Args:
        text: Input text to check.

    Returns:
        True if text contains Hebrew characters.
    """
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
    return bool(hebrew_pattern.search(text))


class GroqService:
    """Service for interacting with Groq API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq service with API key.

        Args:
            api_key: Groq API key. If None, fetches from settings.
        """
        self.api_key = api_key or settings.groq_api_key
        if not self.api_key:
            raise ValueError("Groq API key not found. Set GROQ_API_KEY in environment or Streamlit secrets.")

        self.client = Groq(api_key=self.api_key)
        self.model = settings.groq_model

    def _build_messages(
        self,
        user_input: str,
        custom_instructions: Optional[str] = None,
        is_hebrew: bool = False
    ) -> list:
        """Build the chat messages for tone rephrasing.

        Args:
            user_input: The text to rephrase.
            custom_instructions: Optional custom tone instructions.
            is_hebrew: Whether the input contains Hebrew text.

        Returns:
            List of message dictionaries.
        """
        system_message = {
            "role": "system",
            "content": (
                "You are an expert linguistic editor and translator. Your task is to process the user's "
                "input and output ONLY a valid JSON object with no additional text, markdown formatting, "
                "or code blocks."
            )
        }

        if is_hebrew:
            user_content = f"""The following text is in Hebrew. First translate it to natural, fluent English, then rephrase the English translation into four distinct styles:

1. Professional: Clear, polite, and suitable for workplace communication.
2. Friendly: Warm, approachable, and casual.
3. Direct: Concise, no filler, straight to the point.
4. Creative: Unique, engaging, and stylized.

Hebrew Text: "{user_input}"

Output MUST be a valid JSON object with these keys:
- "translation": The direct English translation of the Hebrew text
- "professional": Professional tone rephrasing (in English)
- "friendly": Friendly tone rephrasing (in English)
- "direct": Direct tone rephrasing (in English)
- "creative": Creative tone rephrasing (in English)

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Respond with ONLY the JSON object, no other text."""
        else:
            user_content = f"""Rephrase the following text into four distinct styles:
1. Professional: Clear, polite, and suitable for workplace communication.
2. Friendly: Warm, approachable, and casual.
3. Direct: Concise, no filler, straight to the point.
4. Creative: Unique, engaging, and stylized.

Text: "{user_input}"

Output MUST be a valid JSON object with these keys:
"professional", "friendly", "direct", "creative".

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Respond with ONLY the JSON object, no other text."""

        user_message = {
            "role": "user",
            "content": user_content
        }

        return [system_message, user_message]

    def rephrase_text(self, user_input: str, custom_instructions: Optional[str] = None) -> Dict[str, str]:
        """Rephrase text into multiple tones. Auto-translates Hebrew to English.

        Args:
            user_input: The text to rephrase (English or Hebrew).
            custom_instructions: Optional custom tone instructions.

        Returns:
            Dictionary with tone keys, rephrased text values, and optional translation.

        Raises:
            Exception: If API call fails or response is invalid.
        """
        try:
            is_hebrew = detect_hebrew(user_input)
            messages = self._build_messages(user_input, custom_instructions, is_hebrew)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                response_format={"type": "json_object"}
            )

            response_text = response.choices[0].message.content.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)

            expected_keys = set(settings.default_tones)
            if not expected_keys.issubset(result.keys()):
                raise ValueError(f"Missing expected keys in response. Expected: {expected_keys}, Got: {set(result.keys())}")

            result["_source_language"] = "hebrew" if is_hebrew else "english"

            return result

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")
