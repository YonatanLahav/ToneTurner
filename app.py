import streamlit as st
from src.services.groq_service import GroqService
from src.components.ui_components import (
    add_to_history,
    apply_dark_mode,
    render_error,
    render_header,
    render_input_section,
    render_results_grid,
    render_sidebar,
)


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="ToneTurner",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    if "results" not in st.session_state:
        st.session_state.results = None
    if "ai_service" not in st.session_state:
        st.session_state.ai_service = None
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "history" not in st.session_state:
        st.session_state.history = []

    # Render sidebar and get dark mode toggle state
    st.session_state.dark_mode = render_sidebar(
        dark_mode=st.session_state.dark_mode,
        history=st.session_state.history
    )

    if st.session_state.dark_mode:
        apply_dark_mode()

    render_header()

    # Input section
    user_input, custom_instructions, output_length = render_input_section()

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        rephrase_clicked = st.button("🔄 Rephrase", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.results = None
            st.rerun()

    # Process rephrasing
    if rephrase_clicked:
        if not user_input or user_input.strip() == "":
            render_error("Please enter some text to rephrase.")
        else:
            try:
                if st.session_state.ai_service is None:
                    with st.spinner("Initializing Groq service..."):
                        st.session_state.ai_service = GroqService()

                with st.spinner("Rephrasing your text... ✍️"):
                    results = st.session_state.ai_service.rephrase_text(
                        user_input=user_input,
                        custom_instructions=custom_instructions,
                        output_length=output_length
                    )
                    st.session_state.results = results
                    st.session_state.history = add_to_history(
                        user_input, results, st.session_state.history
                    )

            except ValueError as e:
                render_error(str(e))
                st.info("💡 Add your Groq API key in `.streamlit/secrets.toml` or set the `GROQ_API_KEY` environment variable.")
            except Exception as e:
                error_msg = str(e).lower()
                if "rate" in error_msg or "quota" in error_msg or "429" in error_msg:
                    render_error("Rate limit reached. Please wait a moment and try again.")
                elif "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                    render_error("Connection issue. Please check your internet and try again.")
                elif "api key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                    render_error("Invalid API key. Please check your Groq API key.")
                else:
                    render_error(f"Failed to rephrase text: {str(e)}")

    # Display results
    if st.session_state.results:
        st.divider()
        render_results_grid(st.session_state.results)


if __name__ == "__main__":
    main()
