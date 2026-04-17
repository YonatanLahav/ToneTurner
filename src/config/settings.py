import os
from dataclasses import dataclass
from typing import List


@dataclass
class AppSettings:
    """Application configuration settings."""

    app_name: str = "ToneTurner"
    app_description: str = "Multi-Tone AI Rephrasing Application"

    # Tone configurations
    default_tones: List[str] = None

    # API settings
    gemini_model: str = "gemini-1.5-flash"
    max_tokens: int = 1024
    temperature: float = 0.7

    # UI settings
    max_input_length: int = 2000

    def __post_init__(self):
        if self.default_tones is None:
            self.default_tones = ["professional", "friendly", "direct", "creative"]

    @property
    def gemini_api_key(self) -> str:
        """Retrieve Gemini API key from environment or Streamlit secrets."""
        try:
            import streamlit as st
            return st.secrets.get("GEMINI_API_KEY", "")
        except:
            return os.getenv("GEMINI_API_KEY", "")


settings = AppSettings()
