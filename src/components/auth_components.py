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

    with st.expander("Or sign in with email"):
        email = st.text_input("Email address", key="magic_link_email")
        if st.button("Send magic link", use_container_width=True):
            if email:
                auth.sign_in_with_magic_link(email)
                st.success("Check your inbox for a login link.")
            else:
                st.warning("Enter your email address.")
