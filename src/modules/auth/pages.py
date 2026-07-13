"""
Authentication router page, handling session timeouts, route protections,
and access denials.
"""

import streamlit as st
import datetime
from src.services.authentication import AuthenticationService


def handle_session_timeout(timeout_minutes: int = 15) -> None:
    """Verifies user session timeout due to inactivity."""
    if st.session_state.get("is_logged_in"):
        if st.session_state.get("remember_me"):
            timeout_minutes = 10080
            
        last_act = st.session_state.get("last_activity")
        if last_act:
            now = datetime.datetime.utcnow()
            diff_seconds = (now - last_act).total_seconds()
            if diff_seconds > (timeout_minutes * 60):
                # Auto logout
                st.session_state["is_logged_in"] = False
                st.session_state["logged_in_user"] = None
                st.session_state["user_role"] = "Customer"
                st.session_state["last_activity"] = None
                st.toast("🕒 Session expired due to inactivity. Please sign in again.", icon="⏰")
                st.rerun()
            else:
                st.session_state["last_activity"] = now
        else:
            st.session_state["last_activity"] = datetime.datetime.utcnow()


def render_access_denied_page(role: str, require_privilege: str) -> None:
    """Displays a detailed, friendly access warning screen with company branding."""
    st.markdown(
        f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 2rem; margin-top: 2rem;">
            <h2 style="color: #EF4444; margin-top: 0; font-size: 2.2rem;">🛡️ Access Denied</h2>
            <p style="color: #FCA5A5; font-size: 1.1rem;">You do not have the required permissions to view this domain.</p>
            <hr style="border-color: rgba(239, 68, 68, 0.2); margin: 1.5rem 0;">
            <ul style="color: #FEE2E2; font-size: 1rem; line-height: 1.8; list-style-type: square; padding-left: 1.5rem;">
                <li><strong>Current User Privilege Level:</strong> <span style="text-transform: uppercase; font-weight: bold; color: #FFF;">{role}</span></li>
                <li><strong>Required Target privilege:</strong> <code>{require_privilege}</code></li>
                <li><strong>Security Action:</strong> Denied access at system routing boundary.</li>
            </ul>
            <p style="color: #F87171; font-size: 0.9rem; margin-top: 1rem;">
                If you believe this is in error, please contact your system administrator to adjust your privilege configurations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def check_route_permission(page: str) -> bool:
    """
    Checks if currently logged in user has access rules to visual page.
    """
    if page in ["Home", "Settings"]:
        return True
        
    logged_user = st.session_state.get("logged_in_user")
    if not logged_user:
        return False
        
    role = logged_user.get("role", "customer")
    
    # Map page to privilege action
    page_to_privilege = {
        "Chatbot": "chatbot",
        "Quotation": "quotation",
        "Claims": "claims",
        "Dashboard": "dashboard",
        "Manager AI": "manager_ai",
        "Monitoring": "monitoring"
    }
    
    req_action = page_to_privilege.get(page)
    if not req_action:
        return True

    if req_action == "monitoring":
        return role.lower().strip() in ["administrator", "admin"]
        
    return AuthenticationService.verify_role_permission(role, req_action)
