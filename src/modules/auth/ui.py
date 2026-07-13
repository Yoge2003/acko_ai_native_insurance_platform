"""
Redesigned enterprise authentication UI.
Premium login card, split-panel layout, demo account grid.
"""

import streamlit as st
import datetime
from src.services.authentication import AuthenticationService
from src.database.session import SessionLocal
from src.repositories.user import UserRepository


def get_auth_service() -> AuthenticationService:
    session = SessionLocal()
    repo = UserRepository(session)
    return AuthenticationService(repo)


# Demo accounts data
_DEMO_ACCOUNTS = [
    ("Administrator", "admin@acko.dev", "AckoAdmin123!", "🔴"),
    ("Manager", "manager@acko.dev", "AckoManager123!", "🟠"),
    ("Underwriter", "underwriter@acko.dev", "AckoUnderwriter123!", "🟡"),
    ("Claims Officer", "claimsofficer@acko.dev", "AckoClaims123!", "🟢"),
    ("Customer", "customer@acko.dev", "AckoCustomer123!", "🔵"),
]


class AuthUI:
    """Renders premium authentication and user profile screens."""

    @staticmethod
    def render_login_page() -> None:
        """Full-page premium enterprise login experience."""

        # Seed demo accounts silently
        try:
            get_auth_service().seed_demo_accounts()
        except Exception:
            pass

        # Inject premium login page styling overrides, glow layers, and animations
        css_content = """
            <div class="acko-login-page-root"></div>
            <div class="login-bg-glow-1"></div>
            <div class="login-bg-glow-2"></div>
            <style>
            /* Center the entire login view */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root)::before {
              content: '';
              position: fixed;
              inset: 0;
              background: linear-gradient(160deg, #0A0A0C 0%, #121214 100%) !important;
              z-index: -2;
            }
            /* Center horizontal block columns */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) div[data-testid="stHorizontalBlock"] {
              max-width: 1200px !important;
              margin: 0 auto !important;
              min-height: calc(100vh - 8rem) !important;
            }
            /* Add padding to the left column's elements natively */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) [data-testid="column"]:has(.login-left-column-marker) {
              padding-right: 2rem !important;
            }
            /* Style right column as the premium Login Card without overriding width/flex */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) [data-testid="column"]:has(.login-right-column-marker) {
              background: rgba(255, 255, 255, 0.03) !important;
              backdrop-filter: blur(28px) !important;
              -webkit-backdrop-filter: blur(28px) !important;
              border: 1px solid rgba(255, 255, 255, 0.08) !important;
              border-radius: 24px !important;
              padding: 40px !important;
              box-shadow: 0 24px 64px rgba(0, 0, 0, 0.7), 0 0 80px rgba(255, 255, 255, 0.01) !important;
            }
            /* Left side styles */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-left-panel {
              display: flex;
              flex-direction: column;
              gap: 1.5rem;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-logo-container {
              display: flex;
              align-items: center;
              gap: 16px;
              margin-bottom: 1rem;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-logo-icon {
              width: 52px;
              height: 52px;
              background: linear-gradient(135deg, #7C3AED, #1DD3B0);
              border-radius: 14px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 26px;
              box-shadow: 0 0 24px rgba(124, 58, 237, 0.5), 0 0 48px rgba(29,211,176,0.15);
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-logo-text {
              display: flex;
              flex-direction: column;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .logo-name {
              font-size: 1.25rem;
              font-weight: 800;
              color: #FFFFFF;
              letter-spacing: -0.02em;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .logo-subtitle {
              font-size: 0.72rem;
              color: #9CA3AF;
              text-transform: uppercase;
              letter-spacing: 0.1em;
              font-weight: 500;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-hero-title {
              font-size: 2.8rem;
              font-weight: 900;
              letter-spacing: -0.05em;
              line-height: 1.1;
              background: linear-gradient(135deg, #FFFFFF 0%, #C4B5FD 45%, #1DD3B0 100%);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              margin: 0;
              filter: drop-shadow(0 0 30px rgba(124,58,237,0.3));
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-hero-subtitle {
              font-size: 0.95rem;
              color: #9CA3AF;
              line-height: 1.65;
              margin: 0 0 1rem 0;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-features-list {
              display: flex;
              flex-direction: column;
              gap: 1rem;
              margin-bottom: 1rem;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .feature-item {
              display: flex;
              align-items: center;
              gap: 16px;
              padding: 0.75rem 1rem;
              background: rgba(255, 255, 255, 0.02);
              border: 1px solid rgba(255, 255, 255, 0.04);
              border-radius: 12px;
              transition: all 0.2s ease;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .feature-item:hover {
              background: rgba(124, 58, 237, 0.08);
              border-color: rgba(124, 58, 237, 0.35);
              transform: translateX(3px);
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .feature-icon {
              width: 36px;
              height: 36px;
              background: rgba(124, 58, 237, 0.12);
              border: 1px solid rgba(124, 58, 237, 0.3);
              border-radius: 10px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 16px;
              box-shadow: 0 0 10px rgba(124,58,237,0.15);
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .feature-desc {
              display: flex;
              flex-direction: column;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .feature-title {
              font-size: 0.85rem;
              font-weight: 600;
              color: #FFFFFF;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .feature-subtitle {
              font-size: 0.75rem;
              color: #9CA3AF;
            }
            /* Decorative illustration panel inside left side */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-left-illustration {
              position: relative;
              width: 100%;
              height: 160px;
              margin-top: 1rem;
              border-radius: 16px;
              background: linear-gradient(135deg, rgba(229, 46, 46, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
              border: 1px solid rgba(255, 255, 255, 0.04);
              overflow: hidden;
              display: flex;
              align-items: center;
              justify-content: center;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .glass-orb-1 {
              position: absolute;
              width: 200px;
              height: 200px;
              background: radial-gradient(circle, rgba(124, 58, 237, 0.25) 0%, rgba(29,211,176,0.1) 50%, transparent 70%);
              border-radius: 50%;
              filter: blur(20px);
              animation: orb-bounce-1 8s ease-in-out infinite alternate;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .glass-orb-2 {
              position: absolute;
              width: 140px;
              height: 140px;
              background: radial-gradient(circle, rgba(29, 211, 176, 0.15) 0%, transparent 70%);
              border-radius: 50%;
              filter: blur(16px);
              animation: orb-bounce-2 10s ease-in-out infinite alternate;
            }
            @keyframes orb-bounce-1 {
              0% { transform: translate(-50px, -20px); }
              100% { transform: translate(50px, 20px); }
            }
            @keyframes orb-bounce-2 {
              0% { transform: translate(40px, 15px); }
              100% { transform: translate(-40px, -15px); }
            }
            /* Background glow elements */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-bg-glow-1 {
              position: fixed;
              top: 5%;
              left: 5%;
              width: 700px;
              height: 700px;
              background: radial-gradient(circle, rgba(124, 58, 237, 0.18) 0%, transparent 65%);
              z-index: -1;
              pointer-events: none;
              filter: blur(60px);
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .login-bg-glow-2 {
              position: fixed;
              bottom: 5%;
              right: 5%;
              width: 600px;
              height: 600px;
              background: radial-gradient(circle, rgba(29, 211, 176, 0.1) 0%, transparent 65%);
              z-index: -1;
              pointer-events: none;
              filter: blur(50px);
            }
            /* Style Inputs Inside Card */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stTextInput input, 
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stNumberInput input {
              height: 48px !important;
              padding: 0 16px !important;
              border-radius: 12px !important;
              border: 1px solid rgba(255, 255, 255, 0.08) !important;
              background: rgba(255, 255, 255, 0.04) !important;
              font-size: 0.9rem !important;
              color: #FFFFFF !important;
              transition: all 0.2s ease !important;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stTextInput input:focus, 
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stNumberInput input:focus {
              border-color: rgba(124, 58, 237, 0.7) !important;
              box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2), 0 0 20px rgba(124,58,237,0.1) !important;
              background: rgba(124, 58, 237, 0.06) !important;
            }
            /* Large Gradient login buttons */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stFormSubmitButton button, 
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stButton button {
              height: 50px !important;
              border-radius: 14px !important;
              background: linear-gradient(135deg, #7C3AED, #5C14CC) !important;
              box-shadow: 0 4px 20px rgba(124, 58, 237, 0.45), 0 0 0 1px rgba(124,58,237,0.2) !important;
              font-weight: 700 !important;
              font-size: 0.95rem !important;
              letter-spacing: -0.01em !important;
              transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stFormSubmitButton button:hover, 
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) .stButton button:hover {
              background: linear-gradient(135deg, #8B47FF, #7C3AED) !important;
              box-shadow: 0 8px 32px rgba(124, 58, 237, 0.6), 0 0 48px rgba(124,58,237,0.15) !important;
              transform: translateY(-2px) !important;
            }
            /* Style Streamlit Tabs Inside Card */
            div[data-testid="stAppViewContainer"]:has(.acko-login-page-root) [data-baseweb="tab-list"] {
              border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
              margin-bottom: 1.5rem !important;
            }
            </style>
        """
        st.markdown(css_content, unsafe_allow_html=True)

        # ── Left brand panel / Right login card ───────────
        left_col, right_col = st.columns([1.2, 1], gap="large")

        with left_col:
            st.markdown('<div class="login-left-column-marker"></div>', unsafe_allow_html=True)
            left_html = """
                <div class="login-left-panel">
                    <div class="login-logo-container">
                        <div class="login-logo-icon">🛡️</div>
                        <div class="login-logo-text">
                            <span class="logo-name">ACKO AI</span>
                            <span class="logo-subtitle">Enterprise Insurance Platform</span>
                        </div>
                    </div>
                    <h1 class="login-hero-title">
                        Enterprise AI for<br>Modern Insurance
                    </h1>
                    <p class="login-hero-subtitle">
                        Experience the modern way of managing underwriting, claims automation, and analytics. Powered by Google Gemini and advanced machine learning models.
                    </p>
                    <div class="login-features-list">
                        <div class="feature-item">
                            <div class="feature-icon">🤖</div>
                            <div class="feature-desc">
                                <span class="feature-title">AI Policy Chatbot</span>
                                <span class="feature-subtitle">RAG and ChromaDB citations</span>
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">💰</div>
                            <div class="feature-desc">
                                <span class="feature-title">Underwriting Prediction</span>
                                <span class="feature-subtitle">ML Premium & SHAP Explainability</span>
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">📄</div>
                            <div class="feature-desc">
                                <span class="feature-title">Vision Claims Triage</span>
                                <span class="feature-subtitle">LangGraph and Computer Vision</span>
                            </div>
                        </div>
                        <div class="feature-item">
                            <div class="feature-icon">🧠</div>
                            <div class="feature-desc">
                                <span class="feature-title">Manager Text-to-SQL</span>
                                <span class="feature-subtitle">Natural language database queries</span>
                            </div>
                        </div>
                    </div>
                    <div class="login-left-illustration">
                        <div class="glass-orb-1"></div>
                        <div class="glass-orb-2"></div>
                    </div>
                </div>
            """
            st.markdown(left_html, unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="login-right-column-marker"></div>', unsafe_allow_html=True)
            right_html = """
                <div class="login-card-header" style="padding: 0 0 1.5rem 0;">
                    <div style="font-size:1.6rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.03em;margin-bottom:6px;font-family:'Poppins',sans-serif;">
                        Welcome back
                    </div>
                    <div style="font-size:0.87rem;color:#9CA3AF;margin-bottom:0;font-family:'Poppins',sans-serif;">
                        Secure enterprise authentication
                    </div>
                </div>
            """
            st.markdown(right_html, unsafe_allow_html=True)

            tab_login, tab_reset, tab_demo = st.tabs(["Sign In", "Reset Password", "Demo Accounts"])

            with tab_login:
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input(
                        "Email Address",
                        placeholder="you@acko.dev",
                        key="login_email_input",
                    ).strip()
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        key="login_pwd_input",
                    )
                    remember_me = st.checkbox("Keep me signed in for 7 days")
                    submitted = st.form_submit_button("Sign In", use_container_width=True)

                    if submitted:
                        if not email or not password:
                            st.error("Please enter both email and password.")
                        else:
                            auth_service = get_auth_service()
                            try:
                                user = auth_service.authenticate(email, password)
                                st.session_state["is_logged_in"] = True
                                st.session_state["logged_in_user"] = {
                                    "id": str(user.id),
                                    "email": user.email,
                                    "full_name": user.full_name,
                                    "role": user.role,
                                }
                                st.session_state["user_role"] = user.role
                                st.session_state["last_activity"] = datetime.datetime.utcnow()
                                st.session_state["remember_me"] = remember_me
                                st.rerun()
                            except Exception as e:
                                st.error(f"Sign in failed: {e}")

            with tab_reset:
                st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
                reset_email = st.text_input(
                    "Registered Email",
                    placeholder="you@acko.dev",
                    key="auth_reset_email",
                ).strip()

                if st.button("Generate Recovery Token", use_container_width=True):
                    if not reset_email:
                        st.error("Please enter your email address.")
                    else:
                        try:
                            token = get_auth_service().generate_reset_token(reset_email)
                            st.session_state["reset_email"] = reset_email
                            st.session_state["reset_token"] = token
                            st.success("Recovery token generated.")
                            st.info(f"**Token:** `{token}`")
                        except Exception as e:
                            st.error(f"Error: {e}")

                if st.session_state.get("reset_token"):
                    st.markdown('<hr style="border-color:#1A1A2E;margin:1rem 0;">', unsafe_allow_html=True)
                    entered_token = st.text_input("Verification Token", key="rt_token")
                    new_password = st.text_input("New Password", type="password", key="rt_newpwd")
                    confirm_password = st.text_input("Confirm New Password", type="password", key="rt_confpwd")

                    if st.button("Reset Password", use_container_width=True):
                        if entered_token != st.session_state["reset_token"]:
                            st.error("Invalid verification token.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            try:
                                get_auth_service().reset_password(
                                    st.session_state["reset_email"], new_password
                                )
                                st.success("Password reset successfully. You can now sign in.")
                                st.session_state["reset_token"] = None
                                st.session_state["reset_email"] = None
                            except Exception as e:
                                st.error(f"Reset failed: {e}")

            with tab_demo:
                st.markdown(
                    '<div style="font-size:0.8rem;color:#475569;margin-bottom:1rem;margin-top:0.5rem;">Use any account below to explore the platform with pre-configured role access.</div>',
                    unsafe_allow_html=True,
                )
                for role, email, pwd, dot in _DEMO_ACCOUNTS:
                    st.markdown(
                        f"""
                        <div class="ds-demo-tag">
                            <div>
                                <div class="ds-demo-role">{dot} {role}</div>
                                <div class="ds-demo-cred">{email}</div>
                            </div>
                            <div class="ds-demo-cred" style="text-align:right;">{pwd}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    '<div style="font-size:0.72rem;color:#2D2D45;margin-top:12px;text-align:center;">Copy credentials above and paste into the Sign In tab.</div>',
                    unsafe_allow_html=True,
                )

    @staticmethod
    def render_user_profile() -> None:
        """Renders the user profile and security settings page."""
        st.markdown(
            """
            <div class="ds-page-header">
                <div class="ds-page-eyebrow">Settings</div>
                <div class="ds-page-title">Account &amp; Security</div>
                <div class="ds-page-subtitle">Manage your profile details and update your security password.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        logged_user = st.session_state.get("logged_in_user")
        if not logged_user:
            st.error("No active session.")
            return

        initials = "".join(p[0].upper() for p in logged_user["full_name"].split()[:2])

        col1, col2 = st.columns([1, 1.2], gap="large")

        with col1:
            st.markdown(
                f"""
                <div class="ds-card" style="text-align:center;padding:2rem;">
                    <div style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,#FF4B4B,#E52E2E);display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700;color:white;margin:0 auto 1.5rem auto;box-shadow:0 0 24px rgba(229,46,46,0.35);">{initials}</div>
                    <div style="font-size:1.1rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.02em;margin-bottom:5px;font-family:'Poppins',sans-serif;">{logged_user['full_name']}</div>
                    <div style="font-size:0.82rem;color:#9CA3AF;margin-bottom:1.25rem;font-family:'Poppins',sans-serif;">{logged_user['email']}</div>
                    <span class="ds-badge ds-badge-brand">{logged_user['role']}</span>
                    <div style="margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid rgba(255,255,255,0.08);">
                        <div style="display:flex;align-items:center;gap:8px;font-size:0.82rem;color:#9CA3AF;font-family:'Poppins',sans-serif;">
                            <span class="ds-status-dot online"></span> Session Active
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown('<div class="ds-section-title">Change Password</div>', unsafe_allow_html=True)
            with st.form("change_password_form"):
                old_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                new_conf = st.text_input("Confirm New Password", type="password")
                chg_btn = st.form_submit_button("Update Password", use_container_width=True)

                if chg_btn:
                    if new_pwd != new_conf:
                        st.error("Passwords do not match.")
                    else:
                        auth_service = get_auth_service()
                        try:
                            auth_service.change_password(logged_user["id"], old_pwd, new_pwd)
                            st.success("Password updated successfully.")
                        except Exception as e:
                            st.error(f"Update failed: {e}")
