from src.models.user import User
from src.repositories.base_history_repo import BaseHistoryRepository
from src.repositories.session_history_repo import SessionHistoryRepository
from src.repositories.supabase_history_repo import SupabaseHistoryRepository


def create_history_repository(user: User | None) -> BaseHistoryRepository:
    if user:
        return SupabaseHistoryRepository(user_id=user.id)
    return SessionHistoryRepository()
