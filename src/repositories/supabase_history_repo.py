from datetime import datetime

import streamlit as st
from supabase import create_client

from src.models.rephrase import RephraseResult
from src.repositories.base_history_repo import BaseHistoryRepository, HistoryEntry

_MAX_HISTORY = 50


def _client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])


class SupabaseHistoryRepository(BaseHistoryRepository):
    """Authenticated-user history persisted in Supabase."""

    def __init__(self, user_id: str):
        self._user_id = user_id

    def add(self, input_text: str, result: RephraseResult) -> None:
        _client().table("rephrase_history").insert({
            "user_id": self._user_id,
            "input_text": input_text,
            "source_language": result.source_language,
            "translation": result.translation,
            "professional": result.professional,
            "friendly": result.friendly,
            "direct": result.direct,
            "creative": result.creative,
        }).execute()

    def all(self) -> list[HistoryEntry]:
        response = (
            _client()
            .table("rephrase_history")
            .select("*")
            .eq("user_id", self._user_id)
            .order("created_at", desc=True)
            .limit(_MAX_HISTORY)
            .execute()
        )
        entries = []
        for row in response.data or []:
            result = RephraseResult(
                professional=row["professional"],
                friendly=row["friendly"],
                direct=row["direct"],
                creative=row["creative"],
                source_language=row["source_language"],
                translation=row.get("translation"),
            )
            ts = datetime.fromisoformat(row["created_at"]).strftime("%H:%M:%S")
            entries.append(HistoryEntry(row["input_text"], result, timestamp=ts))
        return entries
