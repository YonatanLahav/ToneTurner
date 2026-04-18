from src.repositories.base_history_repo import BaseHistoryRepository, HistoryEntry
from src.repositories.session_history_repo import SessionHistoryRepository

HistoryRepository = SessionHistoryRepository

__all__ = ["HistoryRepository", "HistoryEntry", "BaseHistoryRepository"]
