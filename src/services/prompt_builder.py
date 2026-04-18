from src.models.rephrase import RephraseRequest

_SYSTEM_PROMPT = (
    "You are an expert linguistic editor and translator. Your task is to process the user's "
    "input and output ONLY a valid JSON object with no additional text, markdown formatting, "
    "or code blocks."
)

_TONE_DEFINITIONS = """
1. Professional: Clear, polite, and suitable for workplace communication.
2. Friendly: Warm, approachable, and casual.
3. Direct: Concise, no filler, straight to the point.
4. Creative: Unique, engaging, and stylized."""

_LENGTH_INSTRUCTIONS: dict[str, str] = {
    "Very Concise":  "Keep each version very short — 1 sentence maximum.",
    "Concise":       "Keep each version brief — 1-2 sentences.",
    "Balanced":      "Keep each version moderate — 2-3 sentences.",
    "Detailed":      "Make each version thorough — 3-4 sentences.",
    "Very Detailed": "Make each version comprehensive — 4-5 sentences with elaboration.",
}


class PromptBuilder:
    """Builds Groq-compatible message lists from a RephraseRequest."""

    def build(self, request: RephraseRequest, is_hebrew: bool) -> list[dict]:
        length = _LENGTH_INSTRUCTIONS.get(
            request.output_length,
            _LENGTH_INSTRUCTIONS["Balanced"]
        )
        extra = f"Additional instructions: {request.custom_instructions}" if request.custom_instructions else ""

        user_content = (
            self._hebrew_prompt(request.text, length, extra)
            if is_hebrew
            else self._english_prompt(request.text, length, extra)
        )

        return [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ]

    def _english_prompt(self, text: str, length: str, extra: str) -> str:
        return f"""Rephrase the following text into four distinct styles:
{_TONE_DEFINITIONS}

Text: "{text}"

Output length: {length}
{extra}

Output MUST be a valid JSON object with keys:
"professional", "friendly", "direct", "creative".

Respond with ONLY the JSON object, no other text."""

    def _hebrew_prompt(self, text: str, length: str, extra: str) -> str:
        return f"""The following text is in Hebrew. First translate it to natural, fluent English, \
then rephrase the translation into four distinct styles:
{_TONE_DEFINITIONS}

Hebrew Text: "{text}"

Output length: {length}
{extra}

Output MUST be a valid JSON object with keys:
"translation", "professional", "friendly", "direct", "creative".

Respond with ONLY the JSON object, no other text."""
