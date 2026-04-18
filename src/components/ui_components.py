import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.config.theme import DARK, LIGHT, build_css


def render_header():
    """Render application header."""
    st.title("🎭 ToneTurner")
    st.markdown(
        "Transform your text into multiple tones instantly. "
        "Supports **Hebrew → English** translation with automatic rephrasing in Professional, Friendly, Direct, and Creative styles."
    )
    st.divider()


def render_input_section() -> Tuple[str, Optional[str], str]:
    """Render input text area, output length slider, and optional custom instructions.

    Returns:
        Tuple of (user_input, custom_instructions, output_length)
    """
    user_input = st.text_area(
        "Enter your text (English or Hebrew):",
        height=150,
        placeholder="Type or paste text in English or Hebrew... / הקלד או הדבק טקסט באנגלית או בעברית",
        max_chars=2000,
        help="Maximum 2000 characters. Hebrew text will be automatically translated to English."
    )

    length_value = st.select_slider(
        "Output Length:",
        options=["Very Concise", "Concise", "Balanced", "Detailed", "Very Detailed"],
        value="Balanced",
        help="Control how long the rephrased versions should be"
    )

    with st.expander("⚙️ Advanced Options"):
        custom_instructions = st.text_input(
            "Custom tone instructions (optional):",
            placeholder="e.g., Use formal language, Avoid jargon, Add humor",
            help="Provide additional instructions to customize the output"
        )

    return user_input, custom_instructions or None, length_value


def render_translation(results: Dict[str, str]):
    """Render translation section if Hebrew was detected."""
    if results.get("_source_language") == "hebrew" and "translation" in results:
        st.info("🌐 Hebrew detected — translated to English automatically")
        with st.expander("📖 View English Translation", expanded=True):
            st.markdown("**English Translation:**")
            translation = results["translation"]
            st.text_area(
                label="translation_output",
                value=translation,
                height=100,
                disabled=True,
                label_visibility="collapsed"
            )
            # Copy button for translation
            if st.button("📋 Copy Translation", key="copy_translation"):
                st.session_state["clipboard_translation"] = translation
                st.success("Translation copied!", icon="✅")
        st.divider()


def render_copy_button(text: str, key: str, label: str):
    """Render a working copy-to-clipboard button using Streamlit's native approach."""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📋 Copy", key=f"copy_{key}", use_container_width=True):
            st.session_state[f"copied_{key}"] = True
    if st.session_state.get(f"copied_{key}"):
        st.code(text, language=None)
        st.caption("⬆️ Select all and copy from above")
        st.session_state[f"copied_{key}"] = False


def render_results_grid(results: Dict[str, str]):
    """Render results in a 2x2 grid layout."""
    render_translation(results)

    st.subheader("Results")

    tone_config = {
        "professional": {"icon": "💼", "title": "Professional"},
        "friendly":     {"icon": "😊", "title": "Friendly"},
        "direct":       {"icon": "🎯", "title": "Direct"},
        "creative":     {"icon": "✨", "title": "Creative"},
    }

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    columns = [row1_col1, row1_col2, row2_col1, row2_col2]
    tones = ["professional", "friendly", "direct", "creative"]

    for col, tone in zip(columns, tones):
        with col:
            config = tone_config[tone]
            st.markdown(f"### {config['icon']} {config['title']}")

            text_value = results.get(tone, "No result available")
            st.text_area(
                label=f"{tone}_output",
                value=text_value,
                height=150,
                disabled=True,
                label_visibility="collapsed",
                key=f"textarea_{tone}"
            )

            if st.button("📋 Copy", key=f"copy_{tone}", use_container_width=True):
                st.code(text_value, language=None)
                st.success("Copied!", icon="✅")


def add_to_history(input_text: str, results: Dict[str, str], history: List[Dict]) -> List[Dict]:
    """Add a rephrase result to history, keeping last 5 entries.

    Args:
        input_text: The original input text.
        results: The rephrase results dict.
        history: Current history list.

    Returns:
        Updated history list.
    """
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "input": input_text[:60] + ("..." if len(input_text) > 60 else ""),
        "results": results,
    }
    return ([entry] + history)[:5]


def render_sidebar(dark_mode: bool = False, history: Optional[List[Dict]] = None) -> bool:
    """Render sidebar with settings, history, and information.

    Returns:
        dark_mode: Current dark mode toggle state.
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        dark_mode = st.toggle("🌙 Dark Mode", value=dark_mode)

        st.divider()

        # History section
        st.subheader("🕓 Recent Rephrases")
        if not history:
            st.caption("No history yet. Rephrase some text to get started.")
        else:
            for i, entry in enumerate(history):
                with st.expander(f"{entry['timestamp']} — {entry['input']}", expanded=False):
                    st.caption("Click below to restore this result.")
                    if st.button("↩️ Restore", key=f"restore_{i}", use_container_width=True):
                        st.session_state.results = entry["results"]
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


def apply_theme(dark_mode: bool):
    """Apply dark or light theme using palette from src/config/theme.py."""
    st.markdown(build_css(DARK if dark_mode else LIGHT), unsafe_allow_html=True)


def render_error(error_message: str):
    """Render error message."""
    st.error(f"⚠️ Error: {error_message}", icon="🚨")
