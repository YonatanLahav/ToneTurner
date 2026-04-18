import streamlit as st
from typing import Dict, Optional, Tuple


COPY_JS = """
<script>
function copyToClipboard(text, btnId) {
    navigator.clipboard.writeText(text).then(function() {
        var btn = document.getElementById(btnId);
        if (btn) {
            btn.innerText = '✅ Copied!';
            setTimeout(function() { btn.innerText = '📋 Copy'; }, 2000);
        }
    });
}
</script>
"""


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
        return user_input, custom_instructions if custom_instructions else None, length_value

    return user_input, None, length_value


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


def render_sidebar(dark_mode: bool = False) -> bool:
    """Render sidebar with settings and information.

    Returns:
        dark_mode: Current dark mode toggle state.
    """
    with st.sidebar:
        st.header("⚙️ Settings")

        dark_mode = st.toggle("🌙 Dark Mode", value=dark_mode)

        st.divider()

        st.subheader("About ToneTurner")
        st.markdown(
            """
            **ToneTurner** helps you communicate better by providing multiple
            tone variations of your text in seconds.

            Perfect for:
            - Email drafting
            - Slack messages
            - Social media posts
            - Professional communications
            """
        )

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


def apply_dark_mode():
    """Inject CSS for dark mode styling."""
    st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stTextArea textarea {
                background-color: #1e2130;
                color: #fafafa;
            }
            .stExpander {
                background-color: #1e2130;
            }
        </style>
    """, unsafe_allow_html=True)


def render_error(error_message: str):
    """Render error message."""
    st.error(f"⚠️ Error: {error_message}", icon="🚨")
