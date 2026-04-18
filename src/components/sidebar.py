import streamlit as st

from src.repositories.history_repo import HistoryRepository


def render_sidebar(dark_mode: bool, history_repo: HistoryRepository) -> bool:
    """Render sidebar. Returns current dark_mode toggle state."""
    with st.sidebar:
        st.header("⚙️ Settings")
        dark_mode = st.toggle("🌙 Dark Mode", value=dark_mode)

        st.divider()

        st.subheader("🕓 Recent Rephrases")
        history = history_repo.all()
        if not history:
            st.caption("No history yet. Rephrase some text to get started.")
        else:
            for i, entry in enumerate(history):
                with st.expander(f"{entry.timestamp} — {entry.preview}", expanded=False):
                    if st.button("↩️ Restore", key=f"restore_{entry.timestamp}", use_container_width=True):
                        st.session_state.results = entry.result
                        st.rerun()

        st.divider()

        st.subheader("How to Use")
        st.markdown(
            """
            1. Enter or paste your text (English or Hebrew)
            2. Adjust the **Output Length** slider
            3. (Optional) Add custom instructions
            4. Click **Rephrase**
            5. Compare and copy your preferred version

            **Hebrew Support:** Hebrew text is automatically
            translated to English, then rephrased in 4 tones.
            """
        )

        st.divider()
        st.caption("Powered by Groq (Llama 3.3 70B)")

    return dark_mode
