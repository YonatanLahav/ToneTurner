import streamlit as st
from typing import Dict, Optional


def render_header():
    """Render application header."""
    st.title("🎭 ToneTurner")
    st.markdown(
        "Transform your text into multiple tones instantly. "
        "Enter your text below and get Professional, Friendly, Direct, and Creative variations."
    )
    st.divider()


def render_input_section() -> tuple[str, Optional[str]]:
    """Render input text area and optional custom instructions.

    Returns:
        Tuple of (user_input, custom_instructions)
    """
    user_input = st.text_area(
        "Enter your text:",
        height=150,
        placeholder="Type or paste the text you want to rephrase...",
        max_chars=2000,
        help="Maximum 2000 characters"
    )

    with st.expander("⚙️ Advanced Options"):
        custom_instructions = st.text_input(
            "Custom tone instructions (optional):",
            placeholder="e.g., Make it more concise, Add technical jargon",
            help="Provide additional instructions to customize the output"
        )
        return user_input, custom_instructions if custom_instructions else None

    return user_input, None


def render_results_grid(results: Dict[str, str]):
    """Render results in a 2x2 grid layout.

    Args:
        results: Dictionary with tone keys and rephrased text values.
    """
    st.subheader("Results")

    # Define tone styling
    tone_config = {
        "professional": {
            "icon": "💼",
            "color": "#1f77b4",
            "title": "Professional"
        },
        "friendly": {
            "icon": "😊",
            "color": "#ff7f0e",
            "title": "Friendly"
        },
        "direct": {
            "icon": "🎯",
            "color": "#2ca02c",
            "title": "Direct"
        },
        "creative": {
            "icon": "✨",
            "color": "#d62728",
            "title": "Creative"
        }
    }

    # Create 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    columns = [row1_col1, row1_col2, row2_col1, row2_col2]
    tones = ["professional", "friendly", "direct", "creative"]

    for col, tone in zip(columns, tones):
        with col:
            config = tone_config[tone]

            # Container with styled header
            st.markdown(f"### {config['icon']} {config['title']}")

            # Display rephrased text
            text_value = results.get(tone, "No result available")
            st.text_area(
                label=f"{tone}_output",
                value=text_value,
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )

            # Copy button
            if st.button(f"📋 Copy", key=f"copy_{tone}", use_container_width=True):
                st.code(text_value, language=None)
                st.success(f"Copied {config['title']} version!", icon="✅")


def render_sidebar():
    """Render sidebar with settings and information."""
    with st.sidebar:
        st.header("About ToneTurner")
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
            1. Enter or paste your text
            2. (Optional) Add custom instructions
            3. Click **Rephrase**
            4. Compare and copy your preferred version
            """
        )

        st.divider()

        st.caption("Powered by Gemini 1.5 Flash")


def render_error(error_message: str):
    """Render error message.

    Args:
        error_message: Error message to display.
    """
    st.error(f"⚠️ Error: {error_message}", icon="🚨")


def render_loading():
    """Render loading state."""
    with st.spinner("Rephrasing your text... ✍️"):
        pass
