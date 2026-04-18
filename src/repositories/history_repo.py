from datetime import datetime
from typing import Optional

import streamlit as st

from src.models.rephrase import RephraseResult

_MAX_HISTORY = 5


class HistoryEntry:
    def __init__(self, input_text: str, result: RephraseResult):
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        self.preview = input_text[:60] + ("..." if len(input_text) > 60 else "")
        self.result = result


class HistoryRepository:
    """Session-scoped history store. Swap the implementation to persist to a DB."""

    _KEY = "rephrase_history"

    def add(self, input_text: str, result: RephraseResult) -> None:
        history = self._load()
        history.insert(0, HistoryEntry(input_text, result))
        st.session_state[self._KEY] = history[:_MAX_HISTORY]

    def all(self) -> list[HistoryEntry]:
        return self._load()

    def _load(self) -> list[HistoryEntry]:
        return list(st.session_state.get(self._KEY, []))
