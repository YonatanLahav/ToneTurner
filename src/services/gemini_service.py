import json
from typing import Dict, Optional
import google.generativeai as genai
from src.config.settings import settings


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service with API key.

        Args:
            api_key: Gemini API key. If None, fetches from settings.
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in environment or Streamlit secrets.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": settings.temperature,
                "max_output_tokens": settings.max_tokens,
            }
        )

    def _build_prompt(self, user_input: str, custom_instructions: Optional[str] = None) -> str:
        """Build the structured prompt for tone rephrasing.

        Args:
            user_input: The text to rephrase.
            custom_instructions: Optional custom tone instructions.

        Returns:
            Formatted prompt string.
        """
        system_instruction = (
            "You are an expert linguistic editor. Your task is to rephrase the user's input into four "
            "specific tones. You must follow the requested JSON schema strictly and ensure no "
            "additional text is included in the response."
        )

        prompt = f"""{system_instruction}

Rephrase the following text into four distinct styles:
1. Professional: Clear, polite, and suitable for workplace communication.
2. Friendly: Warm, approachable, and casual.
3. Direct: Concise, no filler, straight to the point.
4. Creative: Unique, engaging, and stylized.

Text: "{user_input}"

Output MUST be a valid JSON object with these keys:
"professional", "friendly", "direct", "creative".

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}"""

        return prompt

    def rephrase_text(self, user_input: str, custom_instructions: Optional[str] = None) -> Dict[str, str]:
        """Rephrase text into multiple tones.

        Args:
            user_input: The text to rephrase.
            custom_instructions: Optional custom tone instructions.

        Returns:
            Dictionary with tone keys and rephrased text values.

        Raises:
            Exception: If API call fails or response is invalid.
        """
        try:
            prompt = self._build_prompt(user_input, custom_instructions)
            response = self.model.generate_content(prompt)

            # Extract text and parse JSON
            response_text = response.text.strip()

            # Handle code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)

            # Validate expected keys
            expected_keys = set(settings.default_tones)
            if not expected_keys.issubset(result.keys()):
                raise ValueError(f"Missing expected keys in response. Expected: {expected_keys}, Got: {set(result.keys())}")

            return result

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")
