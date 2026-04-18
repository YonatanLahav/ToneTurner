import streamlit as st

from src.models.user import User
from src.services.auth_service import AuthService


def render_auth_section(auth: AuthService) -> None:
    user = auth.current_user()
    if user:
        _render_user_info(user, auth)
    else:
        _render_login(auth)


def _render_user_info(user: User, auth: AuthService) -> None:
    name = user.name or user.email
    st.caption(f"Signed in as **{name}**")
    if st.button("Sign Out", use_container_width=True):
        auth.sign_out()
        st.rerun()


def _render_login(auth: AuthService) -> None:
    st.caption("Sign in to save history across devices.")

    if st.button("Sign in with Google", use_container_width=True):
        url = auth.sign_in_with_google()
        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
        st.stop()

    with st.expander("Or use email (no password needed)"):
        st.caption("Works for both sign-up and sign-in — we'll email you a magic link.")
        email = st.text_input("Email address", key="magic_link_email")
        if st.button("Send magic link", use_container_width=True):
            if email:
                try:
                    auth.sign_in_with_magic_link(email)
                    st.session_state["magic_link_sent"] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to send link: {e}")
            else:
                st.warning("Enter your email address.")

    if st.session_state.get("magic_link_sent"):
        st.success("✅ Magic link sent! Check your inbox and click the link to sign in.")
        if st.button("Resend", use_container_width=True):
            st.session_state.pop("magic_link_sent", None)
            st.rerun()
