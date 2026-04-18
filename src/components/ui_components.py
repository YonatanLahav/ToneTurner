import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Tuple

from src.config.theme import DARK, LIGHT, build_css
from src.models.rephrase import RephraseRequest, RephraseResult


def render_header():
    st.title("🎭 ToneTurner")
    st.markdown(
        "Transform your text into multiple tones instantly. "
        "Supports **Hebrew → English** translation with automatic rephrasing in "
        "Professional, Friendly, Direct, and Creative styles."
    )
    st.divider()


def render_input_section() -> Tuple[RephraseRequest, bool]:
    """Render input area and controls.

    Returns:
        Tuple of (RephraseRequest, submitted) where submitted is True when
        the Rephrase button was clicked.
    """
    text = st.text_area(
        "Enter your text (English or Hebrew):",
        height=150,
        placeholder="Type or paste text in English or Hebrew... / הקלד או הדבק טקסט באנגלית או בעברית",
        max_chars=2000,
        help="Maximum 2000 characters. Hebrew text will be automatically translated to English.",
    )

    output_length = st.select_slider(
        "Output Length:",
        options=["Very Concise", "Concise", "Balanced", "Detailed", "Very Detailed"],
        value="Balanced",
        help="Control how long the rephrased versions should be",
    )

    with st.expander("⚙️ Advanced Options"):
        custom_instructions = st.text_input(
            "Custom tone instructions (optional):",
            placeholder="e.g., Use formal language, Avoid jargon, Add humor",
            help="Provide additional instructions to customize the output",
        )

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        submitted = st.button("🔄 Rephrase", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.results = None
            st.rerun()

    request = RephraseRequest(
        text=text,
        output_length=output_length,
        custom_instructions=custom_instructions or None,
    )
    return request, submitted


def render_results(result: RephraseResult):
    """Render translation banner (if Hebrew) and 2x2 tone grid."""
    _render_translation(result)

    st.subheader("Results")

    tone_config = {
        "professional": ("💼", "Professional"),
        "friendly":     ("😊", "Friendly"),
        "direct":       ("🎯", "Direct"),
        "creative":     ("✨", "Creative"),
    }

    (col1, col2), (col3, col4) = st.columns(2), st.columns(2)
    for col, (key, (icon, title)) in zip(
        [col1, col2, col3, col4], tone_config.items()
    ):
        with col:
            st.markdown(f"### {icon} {title}")
            value = getattr(result, key, "")
            st.text_area(
                label=key,
                value=value,
                height=150,
                disabled=True,
                label_visibility="collapsed",
                key=f"textarea_{key}",
            )
            _copy_button(value, key=f"copy_{key}")


def _copy_button(text: str, key: str):
    """Render a true one-click clipboard copy button using injected HTML/JS."""
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    components.html(f"""
        <button onclick="
            navigator.clipboard.writeText(`{safe}`).then(() => {{
                this.innerText = '✅ Copied!';
                this.style.backgroundColor = '#22c55e';
                this.style.color = 'white';
                setTimeout(() => {{
                    this.innerText = '📋 Copy';
                    this.style.backgroundColor = '';
                    this.style.color = '';
                }}, 2000);
            }});
        " style="
            width: 100%;
            padding: 6px 12px;
            cursor: pointer;
            border: 1px solid #d0d0d8;
            border-radius: 6px;
            font-size: 14px;
            background-color: transparent;
            transition: background-color 0.2s;
        ">📋 Copy</button>
    """, height=40)


def render_error(message: str):
    st.error(f"⚠️ {message}", icon="🚨")


def apply_theme(dark_mode: bool):
    """Apply dark or light theme using palette from src/config/theme.py."""
    st.markdown(build_css(DARK if dark_mode else LIGHT), unsafe_allow_html=True)


# ── private ──────────────────────────────────────────────────────────────────

def _render_translation(result: RephraseResult):
    if result.source_language != "hebrew" or not result.translation:
        return
    st.info("🌐 Hebrew detected — translated to English automatically")
    with st.expander("📖 View English Translation", expanded=True):
        st.text_area(
            label="translation_output",
            value=result.translation,
            height=100,
            disabled=True,
            label_visibility="collapsed",
        )
        _copy_button(result.translation, key="copy_translation")
    st.divider()
