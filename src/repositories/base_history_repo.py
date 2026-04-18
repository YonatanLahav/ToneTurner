from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.models.rephrase import RephraseResult


class HistoryEntry:
    def __init__(
        self,
        input_text: str,
        result: RephraseResult,
        timestamp: Optional[str] = None,
    ):
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        self.preview = input_text[:60] + ("..." if len(input_text) > 60 else "")
        self.result = result


class BaseHistoryRepository(ABC):
    @abstractmethod
    def add(self, input_text: str, result: RephraseResult) -> None: ...

    @abstractmethod
    def all(self) -> list[HistoryEntry]: ...
