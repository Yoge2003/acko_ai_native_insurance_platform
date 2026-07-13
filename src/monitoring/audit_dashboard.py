"""
Redesigned Enterprise Monitoring Audit Dashboard using the ACKO Design System.
Administrator-only access. Provides health checks, resource telemetry, MLOps metrics, and log inspection.
"""

import streamlit as st
from src.monitoring.system_health import get_system_health_report
from src.monitoring.metrics import MLOpsMetrics
from src.monitoring.log_manager import LogManager


def _health_badge(status: str) -> str:
    if status == "healthy":
        return '<span class="ds-badge ds-badge-success">Healthy</span>'
    elif status == "degraded":
        return '<span class="ds-badge ds-badge-warning">Degraded</span>'
    else:
        return '<span class="ds-badge ds-badge-danger">Offline</span>'


def _gauge_color(pct: float) -> str:
    if pct < 50:
        return "#22C55E"
    elif pct < 80:
        return "#F59E0B"
    return "#EF4444"


def render_audit_dashboard() -> None:
    """Renders the administrator-only DS-styled observability dashboard."""
    st.markdown(
        """
        <div class="ds-page-header">
            <div class="ds-page-eyebrow">Admin Only · Monitoring & Observability</div>
            <div class="ds-page-title">System Health Center</div>
            <div class="ds-page-subtitle">Real-time service health checks, hardware telemetry, MLOps metrics, and rotating log inspection.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_role = st.session_state.get("user_role", "").lower().strip()
    if user_role not in ["admin", "administrator"]:
        st.error("Access Denied — Administrator privileges required.")
        return

    with st.spinner("Fetching diagnostics…"):
        report = get_system_health_report()
        ml_report = MLOpsMetrics.get_metrics_report()

    # ── Overall status banner ──────────────────────────
    overall = report["status"]
    banner_color = "#22C55E" if overall == "healthy" else "#F59E0B" if overall == "degraded" else "#EF4444"
    st.markdown(
        f"""
        <div style="background:rgba({','.join(['34,197,94' if overall=='healthy' else '245,158,11' if overall=='degraded' else '239,68,68'][0].split(','))},0.08);border:1px solid rgba({','.join(['34,197,94' if overall=='healthy' else '245,158,11' if overall=='degraded' else '239,68,68'][0].split(','))},0.2);border-radius:10px;padding:14px 20px;margin-bottom:1.5rem;display:flex;align-items:center;gap:12px;">
            <span class="ds-status-dot {'online' if overall=='healthy' else 'warning' if overall=='degraded' else 'offline'}"></span>
            <span style="font-size:0.9rem;font-weight:600;color:#F1F5F9;">Platform Status: {overall.upper()}</span>
            <span style="margin-left:auto;font-size:0.75rem;color:#475569;">Auto-refreshes on page reload</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Service Health ─────────────────────────────────
    st.markdown('<div class="ds-section-title">Service Health</div>', unsafe_allow_html=True)
    services = [
        ("PostgreSQL", report["database"]["status"], report["database"].get("message", "")),
        ("ChromaDB", report["chromadb"]["status"], report["chromadb"].get("message", "")),
        ("Gemini API", report["gemini"]["status"], report["gemini"].get("message", "")),
        ("ML Models", report["ml_models"]["status"], report["ml_models"].get("message", "")),
    ]
    cols = st.columns(4)
    for col, (name, status, msg) in zip(cols, services):
        with col:
            dot_class = "online" if status == "healthy" else "warning" if status == "degraded" else "offline"
            st.markdown(
                f"""
                <div class="ds-health-item" style="flex-direction:column;align-items:flex-start;gap:6px;">
                    <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;">{name}</div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span class="ds-status-dot {dot_class}"></span>
                        <span style="font-size:0.85rem;font-weight:600;color:#F1F5F9;">{status.upper()}</span>
                    </div>
                    {f'<div style="font-size:0.72rem;color:#475569;margin-top:2px;">{msg[:50]}</div>' if msg else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Hardware Telemetry ─────────────────────────────
    st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">Hardware Telemetry</div>', unsafe_allow_html=True)

    cpu = report["resources"]["cpu"]
    mem = report["resources"]["memory"]
    disk = report["resources"]["disk"]

    tc1, tc2, tc3 = st.columns(3)
    for col, (label, pct, detail) in zip(
        [tc1, tc2, tc3],
        [
            ("CPU Usage", cpu["percent"], f"{cpu['cores_physical']} physical cores · {cpu['cores_logical']} logical"),
            ("Memory Usage", mem["percent"], f"{mem['used_gb']} GB / {mem['total_gb']} GB used"),
            ("Disk Usage", disk["percent"], f"{disk['free_gb']} GB free of {disk['total_gb']} GB"),
        ],
    ):
        with col:
            color = _gauge_color(pct)
            st.markdown(
                f"""
                <div class="ds-monitor-gauge">
                    <div class="ds-monitor-gauge-label">{label}</div>
                    <div class="ds-monitor-gauge-value" style="color:{color};">{pct:.0f}%</div>
                    <div style="height:4px;background:#1A1A2E;border-radius:2px;margin:10px 0;">
                        <div style="height:100%;width:{min(pct,100):.0f}%;background:{color};border-radius:2px;"></div>
                    </div>
                    <div style="font-size:0.72rem;color:#475569;">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── MLOps Metrics ─────────────────────────────────
    st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">MLOps Metrics</div>', unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric("Total Predictions", str(ml_report["predictions_total"]))
    with mc2:
        st.metric("Failed Predictions", str(ml_report["predictions_failed"]))
    with mc3:
        st.metric("Avg Latency", f"{ml_report['avg_latency_ms']} ms")
    with mc4:
        st.metric("p95 Latency", f"{ml_report['p95_latency_ms']} ms")

    mc5, mc6, mc7 = st.columns(3)
    with mc5:
        st.metric("Claims Processed", str(ml_report["claims"]["total"]))
    with mc6:
        st.metric("Policies Issued", str(ml_report["premiums"]["policies_count"]))
    with mc7:
        st.metric("Claims Approval Rate", f"{ml_report['claims']['approval_rate']}%")

    # ── Log Inspector ─────────────────────────────────
    st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">Log Inspector</div>', unsafe_allow_html=True)

    lc1, lc2 = st.columns([1, 3])
    with lc1:
        log_domain = st.selectbox(
            "Domain",
            options=["System", "Auth", "Prediction", "Claims", "Quotation", "RAG", "Manager AI", "Database", "Dashboard"],
            label_visibility="collapsed",
        )
        lines_count = st.slider("Lines", min_value=10, max_value=200, value=50, step=10, label_visibility="collapsed")

    with lc2:
        with st.spinner("Loading logs…"):
            logs = LogManager.get_recent_logs(log_domain, lines_count)

        if logs:
            log_html = ""
            for line in logs:
                if any(k in line for k in ["ERROR", "CRITICAL", "FAIL"]):
                    css = "log-error"
                elif "WARNING" in line or "WARN" in line:
                    css = "log-warn"
                elif any(k in line for k in ["OK", "SUCCESS", "healthy"]):
                    css = "log-ok"
                else:
                    css = "log-info"
                log_html += f'<div class="{css}">{line}</div>'

            st.markdown(f'<div class="ds-log-viewer">{log_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="padding:1rem;color:#2D2D45;font-size:0.82rem;background:#0D0D14;border:1px solid #1A1A2E;border-radius:8px;">No logs recorded yet for domain \'{log_domain}\'.</div>',
                unsafe_allow_html=True,
            )

    # ── Recent Errors ─────────────────────────────────
    st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">Critical Errors</div>', unsafe_allow_html=True)
    sys_logs = LogManager.get_recent_logs("system", 200)
    errors = [l for l in sys_logs if any(kw in l for kw in ["ERROR", "CRITICAL", "FAIL", "Exception"])]
    if errors:
        st.warning(f"**{len(errors)} critical entries found:**\n\n" + "\n".join(errors[:10]))
    else:
        st.success("No critical faults or exceptions in recent logs.")
