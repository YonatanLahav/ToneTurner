import streamlit as st
from src.services.groq_service import GroqService
from src.components.ui_components import (
    render_header,
    render_input_section,
    render_results_grid,
    render_sidebar,
    render_error
)


def main():
    """Main application entry point."""
    # Page configuration
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

    # Render UI
    render_sidebar()
    render_header()

    # Input section
    user_input, custom_instructions = render_input_section()

    # Rephrase button
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
                # Initialize Groq service
                if st.session_state.ai_service is None:
                    with st.spinner("Initializing Groq service..."):
                        st.session_state.ai_service = GroqService()

                # Call API
                with st.spinner("Rephrasing your text... ✍️"):
                    results = st.session_state.ai_service.rephrase_text(
                        user_input=user_input,
                        custom_instructions=custom_instructions
                    )
                    st.session_state.results = results

            except ValueError as e:
                render_error(str(e))
                st.info("💡 Add your Groq API key in `.streamlit/secrets.toml` or set the `GROQ_API_KEY` environment variable.")
            except Exception as e:
                render_error(f"Failed to rephrase text: {str(e)}")

    # Display results
    if st.session_state.results:
        st.divider()
        render_results_grid(st.session_state.results)


if __name__ == "__main__":
    main()
