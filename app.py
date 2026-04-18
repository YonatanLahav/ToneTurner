import streamlit as st

from src.components.sidebar import render_sidebar
from src.components.ui_components import apply_theme, render_error, render_header, render_input_section, render_results
from src.repositories.factory import create_history_repository
from src.services.auth_service import AuthService
from src.services.groq_service import GroqService


def _get_service() -> GroqService:
    if "ai_service" not in st.session_state or st.session_state.ai_service is None:
        service = GroqService()
        st.session_state.ai_service = service
    return st.session_state.ai_service


def main():
    st.set_page_config(
        page_title="ToneTurner",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "results" not in st.session_state:
        st.session_state.results = None

    auth = AuthService()
    auth.handle_callback()

    history_repo = create_history_repository(auth.current_user())

    st.session_state.dark_mode = render_sidebar(
        dark_mode=st.session_state.dark_mode,
        history_repo=history_repo,
        auth=auth,
    )
    apply_theme(st.session_state.dark_mode)

    render_header()

    request, submitted = render_input_section()

    if submitted:
        if not request.text.strip():
            render_error("Please enter some text to rephrase.")
        else:
            try:
                with st.spinner("Rephrasing your text... ✍️"):
                    result = _get_service().rephrase(request)
                st.session_state.results = result
                history_repo.add(request.text, result)

            except ValueError as e:
                st.session_state.ai_service = None
                render_error(str(e))
                st.info(
                    "💡 Add your Groq API key in `.streamlit/secrets.toml` "
                    "or set the `GROQ_API_KEY` environment variable."
                )
            except Exception as e:
                msg = str(e).lower()
                if any(k in msg for k in ("rate", "quota", "429")):
                    render_error("Rate limit reached. Please wait a moment and try again.")
                elif any(k in msg for k in ("connection", "timeout", "network")):
                    render_error("Connection issue. Please check your internet and try again.")
                elif any(k in msg for k in ("api key", "unauthorized", "401")):
                    render_error("Invalid API key. Please check your Groq API key.")
                else:
                    render_error(f"Unexpected error: {e}")

    if st.session_state.results:
        st.divider()
        render_results(st.session_state.results)


if __name__ == "__main__":
    main()
