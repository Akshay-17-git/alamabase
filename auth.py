import streamlit as st
from db import create_user, verify_user

def login_page():
    """Display the login/signup page."""
    st.title("🛡️ SentraShield QA Tool")
    st.markdown("AI-powered security questionnaire answering system")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                user_id = verify_user(email, password)
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.session_state["email"] = email
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please check your email and password.")

    with tab2:
        new_email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        new_password = st.text_input("Password", type="password", key="signup_pass", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Confirm your password")
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if not new_email or not new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if create_user(new_email, new_password):
                    st.success("✅ Account created successfully! Please log in.")
                else:
                    st.error("An account with this email already exists.")

def check_authentication():
    """Check if user is authenticated."""
    return "user_id" in st.session_state and st.session_state.get("user_id") is not None

def require_auth():
    """Require authentication, redirect to login if not authenticated."""
    if not check_authentication():
        login_page()
        st.stop()

def logout():
    """Log out the current user."""
    st.session_state.clear()
    st.rerun()
