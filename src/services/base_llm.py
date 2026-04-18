from abc import ABC, abstractmethod
from src.models.rephrase import RephraseRequest, RephraseResult


class BaseLLM(ABC):
    """Abstract interface for LLM providers. Implement this to add a new provider."""

    @abstractmethod
    def rephrase(self, request: RephraseRequest) -> RephraseResult:
        """Rephrase text according to the request and return a typed result."""
        ...
