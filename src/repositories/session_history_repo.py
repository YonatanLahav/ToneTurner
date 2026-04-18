import streamlit as st

from src.models.rephrase import RephraseResult
from src.repositories.base_history_repo import BaseHistoryRepository, HistoryEntry

_MAX_HISTORY = 5
_KEY = "rephrase_history"


class SessionHistoryRepository(BaseHistoryRepository):
    """Guest-mode: history lives in session state only."""

    def add(self, input_text: str, result: RephraseResult) -> None:
        history = self._load()
        history.insert(0, HistoryEntry(input_text, result))
        st.session_state[_KEY] = history[:_MAX_HISTORY]

    def all(self) -> list[HistoryEntry]:
        return self._load()

    def _load(self) -> list[HistoryEntry]:
        return list(st.session_state.get(_KEY, []))
