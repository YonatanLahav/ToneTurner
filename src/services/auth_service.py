from typing import Optional

import streamlit as st
from supabase import Client, create_client

from src.models.user import User


def _get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)


class AuthService:
    """Wraps Supabase auth. Stores session in st.session_state."""

    _SESSION_KEY = "auth_session"
    _USER_KEY = "auth_user"

    def current_user(self) -> Optional[User]:
        return st.session_state.get(self._USER_KEY)

    def is_authenticated(self) -> bool:
        return self.current_user() is not None

    def sign_in_with_google(self) -> str:
        """Returns the OAuth redirect URL; caller must redirect the browser."""
        client = _get_client()
        response = client.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": st.secrets.get("AUTH_REDIRECT_URL", "")}}
        )
        return response.url

    def sign_in_with_magic_link(self, email: str) -> None:
        client = _get_client()
        client.auth.sign_in_with_otp({"email": email})

    def handle_callback(self) -> bool:
        """
        Call this on every page load. Reads the access_token from query params
        (Supabase OAuth callback), exchanges it for a session, and stores the user.
        Returns True if a new session was established.
        """
        params = st.query_params
        access_token = params.get("access_token")
        refresh_token = params.get("refresh_token")

        if not access_token:
            return False

        try:
            client = _get_client()
            session = client.auth.set_session(access_token, refresh_token or "")
            if session and session.user:
                user_data = session.user
                st.session_state[self._USER_KEY] = User(
                    id=user_data.id,
                    email=user_data.email,
                    name=user_data.user_metadata.get("full_name"),
                    avatar_url=user_data.user_metadata.get("avatar_url"),
                )
                st.session_state[self._SESSION_KEY] = session
                st.query_params.clear()
                return True
        except Exception:
            pass
        return False

    def restore_session(self) -> bool:
        """Restore a previously stored session from session_state (already done if key exists)."""
        return self._USER_KEY in st.session_state

    def sign_out(self) -> None:
        try:
            client = _get_client()
            client.auth.sign_out()
        except Exception:
            pass
        st.session_state.pop(self._USER_KEY, None)
        st.session_state.pop(self._SESSION_KEY, None)
        st.session_state.pop("rephrase_history", None)
