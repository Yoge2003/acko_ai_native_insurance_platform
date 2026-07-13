"""
Main entry point for the ACKO AI Native Insurance Platform.
Handles Streamlit configuration, design system injection, navigation, and page routing.
"""

import sys
import logging
import streamlit as st

logger = logging.getLogger(__name__)

try:
    from src.config.settings import settings
    from src.config.constants import APP_NAME, APP_VERSION
except Exception as e:
    logger.critical(f"Startup Configuration Failure: {e}")
    st.error(f"Startup Configuration Failure: {e}")
    sys.exit(1)

st.set_page_config(
    page_title="ACKO — AI Insurance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state defaults
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Customer"
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False


def inject_custom_styles() -> None:
    """Injects the unified design system CSS from the central design_system module."""
    from src.assets.design_system import inject_design_system
    inject_design_system()


def render_sidebar() -> str:
    """Renders the ultra-premium sidebar navigation. Returns the selected page key."""
    with st.sidebar:
        logged_user = st.session_state.get("logged_in_user", {})
        user_name = logged_user.get("full_name", "Guest") if logged_user else "Guest"
        user_role = st.session_state.get("user_role", "Customer")
        _role = user_role.lower().strip()
        is_admin = _role in ["admin", "administrator"]
        current_page = st.session_state.get("current_page", "Home")

        # ── Brand Logo Block ──────────────────────────────────
        st.markdown(
            """
            <div class="esb-logo">
                <div class="esb-logo-icon">🛡️</div>
                <div>
                    <div class="esb-logo-name">ACKO AI</div>
                    <div class="esb-logo-sub">Enterprise Insurance Platform</div>
                </div>
            </div>
            <div class="esb-logo-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation Groups ─────────────────────────────────
        pages = ["Home", "Chatbot", "Quotation", "Claims", "Dashboard", "Manager AI"]
        if is_admin:
            pages.append("Monitoring")

        page_mapping = {
            "🏠  Home": "Home",
            "🤖  AI Chatbot": "Chatbot",
            "💰  Quotation": "Quotation",
            "📄  Claims": "Claims",
            "📊  Analytics": "Dashboard",
            "🧠  Manager AI": "Manager AI",
            "📈  Monitoring": "Monitoring",
        }

        nav_groups = {
            "MAIN": ["🏠  Home"],
            "AI MODULES": ["🤖  AI Chatbot", "💰  Quotation", "📄  Claims"],
            "INTELLIGENCE": ["📊  Analytics", "🧠  Manager AI"],
            "SYSTEM": ["📈  Monitoring"] if is_admin else [],
        }

        inverse_mapping = {v: k for k, v in page_mapping.items()}
        selected_page = current_page

        for group_label, group_items in nav_groups.items():
            if not group_items:
                continue
            st.markdown(
                f'<div class="esb-group-label">{group_label}</div>',
                unsafe_allow_html=True,
            )
            for display_key in group_items:
                page_key = page_mapping.get(display_key)
                if page_key not in pages:
                    continue
                is_active = (page_key == current_page)
                if is_active:
                    st.markdown('<div class="esb-active" style="display:none;height:0;"></div>', unsafe_allow_html=True)
                if st.button(display_key, use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state["current_page"] = page_key
                    st.rerun()

        # ── User Info Footer ──────────────────────────────────
        st.markdown('<div class="esb-footer-divider"></div>', unsafe_allow_html=True)

        initials = "".join(p[0].upper() for p in user_name.split()[:2]) if user_name and user_name != "Guest" else "G"
        import datetime
        if "session_login_time" not in st.session_state:
            st.session_state["session_login_time"] = datetime.datetime.now().strftime("%I:%M %p")

        role_badge_color = {
            "admin": "#FF4757", "administrator": "#FF4757",
            "manager": "#F0B254", "underwriter": "#A855F7",
            "claims officer": "#1DD3B0", "customer": "#7C3AED",
        }.get(_role, "#7C3AED")

        st.markdown(
            f"""
            <div class="esb-user-card">
                <div class="esb-user-avatar" style="background: linear-gradient(135deg, {role_badge_color}, #1DD3B0);">{initials}</div>
                <div style="flex:1;min-width:0;">
                    <div class="esb-user-name">{user_name}</div>
                    <div class="esb-user-meta">
                        <div class="esb-online-dot"></div>
                        <div class="esb-user-role">{user_role}</div>
                    </div>
                    <div style="font-size:0.55rem;color:rgba(255,255,255,0.25);margin-top:3px;font-family:'JetBrains Mono',monospace;">
                        Session · {st.session_state.get('session_login_time', '—')}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("is_logged_in"):
            st.markdown('<div class="esb-logout-marker" style="display:none;height:0;"></div>', unsafe_allow_html=True)
            if st.button("⇠ Sign Out", use_container_width=True, key="logout_btn"):
                from src.modules.auth.ui import get_auth_service
                auth_serv = get_auth_service()
                lu = st.session_state.get("logged_in_user", {})
                auth_serv.logout(lu.get("email"), lu.get("role"))
                st.session_state["is_logged_in"] = False
                st.session_state["logged_in_user"] = None
                st.session_state["user_role"] = "Customer"
                st.session_state["last_activity"] = None
                st.rerun()

        st.markdown(
            f'<div class="esb-version">ACKO AI · v{APP_VERSION} · Enterprise</div>',
            unsafe_allow_html=True,
        )

    return selected_page


def render_home_page() -> None:
    """Renders the ultra-premium Home landing page."""

    # ── HERO ───────────────────────────────────────────────────
    st.markdown(
        """
        <div class="ds-hero">
            <div class="ds-hero-orb"></div>
            <div class="ds-hero-orb-2"></div>
            <div class="ds-hero-eyebrow">✦ ACKO AI Native Insurance Platform &nbsp;·&nbsp; Enterprise Grade</div>
            <div class="ds-hero-title">Autonomous AI for<br>Modern Insurance</div>
            <div class="ds-hero-sub">
                The complete AI-native insurance operations platform — autonomous underwriting, 
                Gemini Vision claims assessment, RAG-powered policy Q&amp;A, and natural language 
                analytics. Built for production. Designed for scale.
            </div>
            <div style="display:flex;gap:10px;margin-top:2rem;flex-wrap:wrap;">
                <div class="ds-stat-chip">🤖 <strong>RAG Chatbot</strong> &nbsp;·&nbsp; ChromaDB + Gemini</div>
                <div class="ds-stat-chip">💰 <strong>ML Underwriting</strong> &nbsp;·&nbsp; Random Forest + SHAP</div>
                <div class="ds-stat-chip">📄 <strong>Vision Claims</strong> &nbsp;·&nbsp; LangGraph + XGBoost</div>
                <div class="ds-stat-chip">🧠 <strong>Manager AI</strong> &nbsp;·&nbsp; Text-to-SQL</div>
                <div class="ds-stat-chip">📊 <strong>Analytics</strong> &nbsp;·&nbsp; Plotly + PostgreSQL</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── MODULE CARDS ───────────────────────────────────────────
    st.markdown(
        '<div class="ds-section-title" style="margin-bottom:1.2rem;">Core AI Modules</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    modules_row1 = [
        {
            "col": col1,
            "icon": "🤖",
            "title": "AI Policy Chatbot",
            "stack": "RAG · ChromaDB · Gemini",
            "badge": "ds-badge-aurora",
            "desc": "Retrieval-Augmented Generation pipeline answers coverage questions with source citations, latency tracking, and token telemetry.",
            "glow": "rgba(29,211,176,0.3)",
            "stat": "911 chunks indexed",
            "stat_color": "#1DD3B0",
        },
        {
            "col": col2,
            "icon": "💰",
            "title": "Premium Quotation",
            "stack": "Random Forest · SHAP",
            "badge": "ds-badge-brand",
            "desc": "ML-driven annual premium prediction with SHAP explainability for every underwriting decision. Trained on 50K+ vehicle records.",
            "glow": "rgba(124,58,237,0.35)",
            "stat": "99.6% model confidence",
            "stat_color": "#A855F7",
        },
        {
            "col": col3,
            "icon": "📄",
            "title": "Claims AI Engine",
            "stack": "Gemini Vision · LangGraph",
            "badge": "ds-badge-warning",
            "desc": "Computer vision damage assessment with fraud scoring, severity classification, and automated triage routing via LangGraph.",
            "glow": "rgba(240,178,84,0.3)",
            "stat": "Auto-routing active",
            "stat_color": "#F0B254",
        },
    ]

    for m in modules_row1:
        with m["col"]:
            st.markdown(
                f"""
                <div class="ds-card" style="min-height:240px;position:relative;">
                    <div class="ds-card-accent"></div>
                    <div style="position:absolute;top:-30px;right:-30px;width:120px;height:120px;
                                border-radius:50%;background:radial-gradient(circle,{m['glow']} 0%,transparent 70%);
                                pointer-events:none;"></div>
                    <div style="font-size:2.2rem;margin-bottom:14px;filter:drop-shadow(0 0 12px {m['glow']});">{m['icon']}</div>
                    <div style="font-size:0.95rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.02em;margin-bottom:8px;">{m['title']}</div>
                    <span class="ds-badge {m['badge']}" style="margin-bottom:14px;display:inline-block;">{m['stack']}</span>
                    <div style="font-size:0.8rem;color:var(--text-secondary);line-height:1.65;margin-bottom:14px;">{m['desc']}</div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:0.7rem;font-weight:600;color:{m['stat_color']};">
                        <span style="width:6px;height:6px;border-radius:50%;background:{m['stat_color']};box-shadow:0 0 6px {m['stat_color']};"></span>
                        {m['stat']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    col4, col5 = st.columns(2, gap="medium")

    modules_row2 = [
        {
            "col": col4,
            "icon": "📊",
            "title": "Analytics Dashboard",
            "stack": "Plotly · PostgreSQL · SQLAlchemy",
            "badge": "ds-badge-info",
            "desc": "Real-time KPI monitoring with interactive Plotly charts, trend analysis, portfolio breakdown, and executive-level reporting that updates live.",
            "glow": "rgba(0,210,255,0.25)",
            "stat": "Live data · Auto-refresh",
            "stat_color": "#00D2FF",
        },
        {
            "col": col5,
            "icon": "🧠",
            "title": "Manager AI",
            "stack": "LangGraph · Text-to-SQL · Gemini",
            "badge": "ds-badge-gold",
            "desc": "Natural language interface that converts plain English into safe, read-only PostgreSQL queries via a LangGraph agent with SQL validation guardrails.",
            "glow": "rgba(245,200,66,0.25)",
            "stat": "Read-only SQL verified",
            "stat_color": "#F5C842",
        },
    ]

    for m in modules_row2:
        with m["col"]:
            st.markdown(
                f"""
                <div class="ds-card" style="position:relative;">
                    <div class="ds-card-accent"></div>
                    <div style="position:absolute;top:-30px;right:-30px;width:140px;height:140px;
                                border-radius:50%;background:radial-gradient(circle,{m['glow']} 0%,transparent 70%);
                                pointer-events:none;"></div>
                    <div style="font-size:2.2rem;margin-bottom:14px;filter:drop-shadow(0 0 12px {m['glow']});">{m['icon']}</div>
                    <div style="font-size:0.95rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.02em;margin-bottom:8px;">{m['title']}</div>
                    <span class="ds-badge {m['badge']}" style="margin-bottom:14px;display:inline-block;">{m['stack']}</span>
                    <div style="font-size:0.8rem;color:var(--text-secondary);line-height:1.65;margin-bottom:14px;">{m['desc']}</div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:0.7rem;font-weight:600;color:{m['stat_color']};">
                        <span style="width:6px;height:6px;border-radius:50%;background:{m['stat_color']};box-shadow:0 0 6px {m['stat_color']};"></span>
                        {m['stat']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── ARCHITECTURE SHOWCASE ──────────────────────────────────
    st.markdown(
        '<div class="ds-section-divider" style="margin-top:2rem;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-title" style="margin-bottom:1.2rem;">Platform Architecture</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background:rgba(12,11,26,0.9);border:1px solid rgba(124,58,237,0.2);
                    border-radius:20px;overflow:hidden;backdrop-filter:blur(16px);
                    box-shadow:0 8px 32px rgba(0,0,0,0.4);">
            <div style="display:grid;grid-template-columns:repeat(4,1fr);">
                <div style="padding:1.4rem 1.2rem;text-align:center;border-right:1px solid rgba(255,255,255,0.05);
                            background:linear-gradient(180deg,rgba(124,58,237,0.07) 0%,transparent 100%);">
                    <div style="font-size:1.8rem;margin-bottom:10px;filter:drop-shadow(0 0 10px rgba(124,58,237,0.5));">🖥️</div>
                    <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;">UI Layer</div>
                    <div style="font-size:0.82rem;font-weight:700;background:linear-gradient(135deg,#C4B5FD,#A855F7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Streamlit Modules</div>
                    <div style="font-size:0.68rem;color:rgba(168,164,192,0.5);margin-top:5px;">6 enterprise pages</div>
                </div>
                <div style="padding:1.4rem 1.2rem;text-align:center;border-right:1px solid rgba(255,255,255,0.05);
                            background:linear-gradient(180deg,rgba(29,211,176,0.05) 0%,transparent 100%);">
                    <div style="font-size:1.8rem;margin-bottom:10px;filter:drop-shadow(0 0 10px rgba(29,211,176,0.4));">⚙️</div>
                    <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;">Service Layer</div>
                    <div style="font-size:0.82rem;font-weight:700;background:linear-gradient(135deg,#1DD3B0,#48D1CC);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Business Logic</div>
                    <div style="font-size:0.68rem;color:rgba(168,164,192,0.5);margin-top:5px;">Domain services + RBAC</div>
                </div>
                <div style="padding:1.4rem 1.2rem;text-align:center;border-right:1px solid rgba(255,255,255,0.05);
                            background:linear-gradient(180deg,rgba(245,200,66,0.04) 0%,transparent 100%);">
                    <div style="font-size:1.8rem;margin-bottom:10px;filter:drop-shadow(0 0 10px rgba(245,200,66,0.4));">🗄️</div>
                    <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;">Data Layer</div>
                    <div style="font-size:0.82rem;font-weight:700;background:linear-gradient(135deg,#F5C842,#F0B254);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">PostgreSQL 17 · ChromaDB</div>
                    <div style="font-size:0.68rem;color:rgba(168,164,192,0.5);margin-top:5px;">SQLAlchemy 2.0 ORM</div>
                </div>
                <div style="padding:1.4rem 1.2rem;text-align:center;
                            background:linear-gradient(180deg,rgba(224,64,251,0.05) 0%,transparent 100%);">
                    <div style="font-size:1.8rem;margin-bottom:10px;filter:drop-shadow(0 0 10px rgba(224,64,251,0.5));">🤖</div>
                    <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;">AI / ML Layer</div>
                    <div style="font-size:0.82rem;font-weight:700;background:linear-gradient(135deg,#E040FB,#A855F7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Gemini · LangGraph · SHAP</div>
                    <div style="font-size:0.68rem;color:rgba(168,164,192,0.5);margin-top:5px;">Random Forest + XGBoost</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── LIVE STATUS TABLE ─────────────────────────────────────
    st.markdown(
        '<div class="ds-section-title" style="margin-top:2rem;margin-bottom:1rem;">Module Status — All Systems Operational</div>',
        unsafe_allow_html=True,
    )

    status_modules = [
        ("🤖", "AI Policy Chatbot",     "RAG · ChromaDB · Gemini 2.0 Flash",         "#1DD3B0"),
        ("💰", "Premium Quotation",     "Random Forest · SHAP · Scikit-Learn",         "#A855F7"),
        ("📄", "Claims AI Engine",      "Gemini Vision · LangGraph · XGBoost",          "#F0B254"),
        ("📊", "Analytics Dashboard",  "Plotly · PostgreSQL 17 · SQLAlchemy 2.0",      "#00D2FF"),
        ("🧠", "Manager AI",           "LangGraph Text-to-SQL · Gemini",               "#F5C842"),
        ("🔐", "Auth & RBAC",          "Bcrypt · Session Guards · 5-Role Model",        "#0ECB81"),
        ("📈", "System Monitoring",    "Psutil · Scipy · Rotating Audit Logs",          "#E040FB"),
    ]

    rows_html = ""
    for icon, name, tech, color in status_modules:
        rows_html += f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:12px 20px;border-bottom:1px solid rgba(255,255,255,0.03);
                    transition:background 0.2s ease;" 
             onmouseover="this.style.background='rgba(124,58,237,0.05)'"
             onmouseout="this.style.background='transparent'">
            <div style="display:flex;align-items:center;gap:12px;flex:1;">
                <span style="font-size:1.2rem;filter:drop-shadow(0 0 8px {color}40);">{icon}</span>
                <div>
                    <div style="font-size:0.85rem;font-weight:600;color:#F0EEF9;">{name}</div>
                    <div style="font-size:0.7rem;color:rgba(168,164,192,0.6);margin-top:2px;font-family:'JetBrains Mono',monospace;">{tech}</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:7px;">
                <span style="width:7px;height:7px;border-radius:50%;background:{color};
                             box-shadow:0 0 8px {color};animation:dot-pulse 2.5s ease-in-out infinite;"></span>
                <span style="font-size:0.68rem;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:0.08em;">Production</span>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div style="background:rgba(12,11,26,0.9);border:1px solid rgba(255,255,255,0.06);
                    border-radius:20px;overflow:hidden;backdrop-filter:blur(16px);
                    box-shadow:0 8px 32px rgba(0,0,0,0.4);">
            <div style="padding:14px 20px 10px 20px;border-bottom:1px solid rgba(255,255,255,0.05);
                        display:flex;align-items:center;gap:8px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#0ECB81;
                             box-shadow:0 0 10px #0ECB81;animation:dot-pulse 2.5s ease-in-out infinite;"></span>
                <span style="font-size:0.65rem;font-weight:700;color:rgba(255,255,255,0.35);
                             text-transform:uppercase;letter-spacing:0.12em;">All 7 Modules Operational</span>
            </div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── TECH STACK FOOTER BADGES ──────────────────────────────
    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;opacity:0.6;padding:1rem 0;">
            <div class="ds-stat-chip">Python 3.11</div>
            <div class="ds-stat-chip">Streamlit</div>
            <div class="ds-stat-chip">SQLAlchemy 2.0</div>
            <div class="ds-stat-chip">PostgreSQL 17</div>
            <div class="ds-stat-chip">ChromaDB</div>
            <div class="ds-stat-chip">Google Gemini</div>
            <div class="ds-stat-chip">LangGraph</div>
            <div class="ds-stat-chip">SHAP</div>
            <div class="ds-stat-chip">Scikit-Learn</div>
            <div class="ds-stat-chip">XGBoost</div>
            <div class="ds-stat-chip">Plotly</div>
            <div class="ds-stat-chip">Alembic</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Main app runner — injects design system, handles auth, routes pages."""
    try:
        inject_custom_styles()

        from src.modules.auth.pages import (
            handle_session_timeout,
            check_route_permission,
            render_access_denied_page,
        )
        handle_session_timeout()

        if not st.session_state.get("is_logged_in"):
            from src.modules.auth.ui import AuthUI
            AuthUI.render_login_page()
            return

        page = render_sidebar()
        logger.info(f"Routing to page: {page}")

        if not check_route_permission(page):
            privilege_label = {
                "Chatbot": "chatbot",
                "Quotation": "quotation",
                "Claims": "claims",
                "Dashboard": "dashboard",
                "Manager AI": "manager_ai",
                "Monitoring": "monitoring",
            }.get(page, page)
            render_access_denied_page(st.session_state["user_role"], privilege_label)
            return

        try:
            if page == "Home":
                render_home_page()
            elif page == "Chatbot":
                from src.modules.chatbot.pages import render_chatbot_page
                render_chatbot_page()
            elif page == "Quotation":
                from src.modules.quotation.pages import render_quotation_page
                render_quotation_page()
            elif page == "Claims":
                from src.modules.claims.pages import render_claims_page
                render_claims_page()
            elif page == "Dashboard":
                from src.modules.dashboard.pages import render_dashboard_page
                render_dashboard_page()
            elif page == "Manager AI":
                from src.modules.manager_ai.pages import render_manager_ai_page
                render_manager_ai_page()
            elif page == "Monitoring":
                from src.monitoring.audit_dashboard import render_audit_dashboard
                render_audit_dashboard()
            elif page in ["Settings", "Profile"]:
                from src.modules.auth.ui import AuthUI
                AuthUI.render_user_profile()
        except Exception as module_err:
            logger.error(f"Failed to render '{page}': {module_err}", exc_info=True)
            st.error("This page encountered an error. Please try again or contact support.")

    except Exception as err:
        logger.critical(f"FATAL: {err}", exc_info=True)
        st.error("A critical error occurred. Please refresh the page.")


if __name__ == "__main__":
    main()
