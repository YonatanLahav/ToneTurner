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

    # Use a hash of the result content so keys change on every new rephrase,
    # forcing Streamlit to re-render the text areas with fresh values.
    result_hash = hash((result.professional, result.friendly, result.direct, result.creative))

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
                key=f"textarea_{key}_{result_hash}",
            )
            _copy_button(value, key=f"copy_{key}_{result_hash}")


def _copy_button(text: str, key: str):
    """Render a one-click clipboard copy button styled to match Streamlit's native buttons."""
    dark = st.session_state.get("dark_mode", False)
    bg        = "#2a2a3a" if dark else "#ffffff"
    color     = "#fafafa" if dark else "#31333f"
    border    = "#4a4a5a" if dark else "#d0d0d8"
    hover_bg  = "#3a3a4f" if dark else "#f0f2f6"
    iframe_bg = "#0e1117" if dark else "#ffffff"

    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    components.html(f"""
        <style>
            body {{ margin: 0; padding: 0; background: {iframe_bg}; }}
            button {{
                width: 100%;
                height: 38px;
                background-color: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: 6px;
                font-size: 14px;
                font-family: "Source Sans Pro", sans-serif;
                font-weight: 400;
                cursor: pointer;
                transition: background-color 0.15s, border-color 0.15s;
            }}
            button:hover {{ background-color: {hover_bg}; border-color: #7c3aed; }}
        </style>
        <button id="btn_{key}" onclick="
            navigator.clipboard.writeText(`{safe}`).then(() => {{
                var btn = document.getElementById('btn_{key}');
                btn.innerText = '✅ Copied!';
                btn.style.backgroundColor = '#22c55e';
                btn.style.color = 'white';
                btn.style.borderColor = '#22c55e';
                setTimeout(() => {{
                    btn.innerText = '📋 Copy';
                    btn.style.backgroundColor = '{bg}';
                    btn.style.color = '{color}';
                    btn.style.borderColor = '{border}';
                }}, 2000);
            }});
        ">📋 Copy</button>
    """, height=46)


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
