import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class AppSettings:
    """Application configuration settings."""

    app_name: str = "ToneTurner"
    app_description: str = "Multi-Tone AI Rephrasing Application"

    # Tone configurations
    default_tones: List[str] = field(
        default_factory=lambda: ["professional", "friendly", "direct", "creative"]
    )

    # API settings
    groq_model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 4096
    temperature: float = 0.7

    # UI settings
    max_input_length: int = 2000

    @property
    def groq_api_key(self) -> str:
        """Retrieve Groq API key from environment or Streamlit secrets."""
        try:
            import streamlit as st
            return st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
        except Exception:
            return os.getenv("GROQ_API_KEY", "")


settings = AppSettings()
