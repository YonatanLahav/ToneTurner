from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RephraseRequest:
    text: str
    output_length: str = "Balanced"
    custom_instructions: Optional[str] = None


@dataclass
class RephraseResult:
    professional: str
    friendly: str
    direct: str
    creative: str
    source_language: str = "english"
    translation: Optional[str] = None

    def tones(self) -> dict[str, str]:
        """Return the four tone variations as a plain dict."""
        return {
            "professional": self.professional,
            "friendly":     self.friendly,
            "direct":       self.direct,
            "creative":     self.creative,
        }

    @classmethod
    def from_dict(cls, data: dict, source_language: str = "english") -> "RephraseResult":
        """Build a RephraseResult from a raw API response dict."""
        return cls(
            professional    = data["professional"],
            friendly        = data["friendly"],
            direct          = data["direct"],
            creative        = data["creative"],
            source_language = source_language,
            translation     = data.get("translation"),
        )
