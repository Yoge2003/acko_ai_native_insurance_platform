"""
ACKO AI Native Insurance Platform — ULTRA-PREMIUM Design System v3.0
=====================================================================
Deep-space glassmorphism with aurora gradients and neon glow effects.

Design Philosophy: "Midnight Aurora" — dark as deep space, alive with
luminous gradients that evoke intelligence and trust.

Palette:
  BG Base:     #03020A  (near-black, deep space)
  BG Surface:  #07060F  (dark indigo surface)
  BG Card:     #0C0B1A  (card background)
  Brand:       #6C2BD9  (vivid violet)
  Brand-2:     #9B59E8  (bright purple)
  Aurora-1:    #1DD3B0  (teal/emerald)
  Aurora-2:    #48D1CC  (light teal)
  Neon-Pink:   #E040FB  (neon magenta)
  Gold:        #F5C842  (premium gold)
  Success:     #0ECB81  (bright green)
  Warning:     #F0B254  (amber)
  Danger:      #FF4757  (vivid red)
  Info:        #00D2FF  (electric blue)
"""

DESIGN_SYSTEM_CSS = """
<style>
/* ─────────────────────────────────────────────────────────────
   FONTS  — Inter (UI) + JetBrains Mono (code)
───────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ─────────────────────────────────────────────────────────────
   GLOBAL DESIGN TOKENS
───────────────────────────────────────────────────────────── */
:root {
  /* Backgrounds */
  --bg-base:        #03020A;
  --bg-surface:     #07060F;
  --bg-card:        #0C0B1A;
  --bg-card-hover:  #100F20;
  --bg-elevated:    #141228;

  /* Brand / Aurora palette */
  --brand:          #7C3AED;
  --brand-2:        #9B59E8;
  --brand-light:    #A855F7;
  --brand-glow:     rgba(124, 58, 237, 0.45);
  --brand-dim:      rgba(124, 58, 237, 0.12);
  --aurora-1:       #1DD3B0;
  --aurora-2:       #48D1CC;
  --aurora-glow:    rgba(29, 211, 176, 0.35);
  --neon-pink:      #E040FB;
  --neon-pink-glow: rgba(224, 64, 251, 0.35);
  --gold:           #F5C842;
  --gold-glow:      rgba(245, 200, 66, 0.3);

  /* Borders */
  --border:         rgba(255,255,255,0.06);
  --border-hover:   rgba(255,255,255,0.14);
  --border-brand:   rgba(124, 58, 237, 0.4);
  --border-aurora:  rgba(29, 211, 176, 0.35);

  /* Semantic */
  --success:        #0ECB81;
  --success-glow:   rgba(14, 203, 129, 0.3);
  --warning:        #F0B254;
  --danger:         #FF4757;
  --info:           #00D2FF;

  /* Text */
  --text-primary:   #F0EEF9;
  --text-secondary: #A8A4C0;
  --text-muted:     #5E5A7A;

  /* Transitions */
  --t-fast:   0.15s cubic-bezier(0.4,0,0.2,1);
  --t-med:    0.25s cubic-bezier(0.4,0,0.2,1);
  --t-slow:   0.4s cubic-bezier(0.4,0,0.2,1);
}

/* ─────────────────────────────────────────────────────────────
   GLOBAL RESET & BASE
───────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg-base) !important;
  color: var(--text-primary) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Immersive background: deep space + aurora glow orbs */
.stApp {
  background:
    radial-gradient(ellipse 80vw 60vh at 10% 5%,  rgba(124,58,237,0.10) 0%, transparent 65%),
    radial-gradient(ellipse 60vw 50vh at 90% 10%, rgba(29,211,176,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 70vw 80vh at 50% 80%, rgba(224,64,251,0.05) 0%, transparent 65%),
    linear-gradient(180deg, #03020A 0%, #050411 50%, #03020A 100%) !important;
}

/* ─────────────────────────────────────────────────────────────
   HIDE STREAMLIT CHROME
───────────────────────────────────────────────────────────── */
#MainMenu, footer, .stDeployButton,
[data-testid="stToolbar"] { display: none !important; }

/* ─────────────────────────────────────────────────────────────
   ULTRA-PREMIUM SCROLLBAR
───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--brand), var(--aurora-1));
  border-radius: 4px;
}

/* ─────────────────────────────────────────────────────────────
   MAIN CONTENT AREA
───────────────────────────────────────────────────────────── */
.main .block-container {
  padding: 2rem 2.5rem 5rem 2.5rem !important;
  max-width: 1500px !important;
  position: relative;
  z-index: 1;
}

/* ══════════════════════════════════════════════════════════════
   SIDEBAR — "Control Tower"
══════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background:
    radial-gradient(ellipse 100% 40% at 50% 0%, rgba(124,58,237,0.12) 0%, transparent 60%),
    linear-gradient(180deg, #06051A 0%, #03020A 100%) !important;
  border-right: 1px solid rgba(124,58,237,0.18) !important;
  backdrop-filter: blur(24px);
}
section[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stButton {
  padding-left: 14px !important;
  padding-right: 14px !important;
}

/* Sidebar logo block */
.esb-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 16px 10px 16px;
}
.esb-logo-icon {
  width: 42px; height: 42px;
  background: linear-gradient(135deg, #7C3AED 0%, #1DD3B0 100%);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
  box-shadow: 0 0 20px rgba(124,58,237,0.5), 0 0 40px rgba(29,211,176,0.15);
}
.esb-logo-name {
  font-size: 1.1rem; font-weight: 800;
  background: linear-gradient(135deg, #FFFFFF 0%, #A78BFA 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; letter-spacing: -0.03em; line-height: 1.1;
}
.esb-logo-sub {
  font-size: 0.6rem; color: var(--text-muted);
  font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase;
  margin-top: 2px;
}
.esb-logo-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(124,58,237,0.4) 50%, transparent 100%);
  margin: 10px 14px;
}

/* Nav Group Labels */
.esb-group-label {
  font-size: 0.6rem; font-weight: 700;
  color: rgba(255,255,255,0.22);
  letter-spacing: 0.15em; text-transform: uppercase;
  margin-top: 18px; margin-bottom: 4px; padding: 0 16px;
}

/* Nav buttons — Streamlit radio reimagined */
section[data-testid="stSidebar"] button {
  background: transparent !important;
  border: 1px solid transparent !important;
  color: var(--text-secondary) !important;
  font-size: 0.82rem !important;
  padding: 10px 14px !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  width: 100% !important;
  justify-content: flex-start !important;
  text-align: left !important;
  transition: all var(--t-med) !important;
  box-shadow: none !important;
  height: auto !important;
  letter-spacing: -0.01em !important;
}
section[data-testid="stSidebar"] button:hover {
  background: rgba(124,58,237,0.1) !important;
  border-color: rgba(124,58,237,0.25) !important;
  color: #FFFFFF !important;
  transform: translateX(3px) !important;
}

/* Active nav item via esb-active marker trick */
div[data-testid="element-container"]:has(.esb-active) + div[data-testid="element-container"] button {
  background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(29,211,176,0.1)) !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(124,58,237,0.5) !important;
  box-shadow: 0 0 16px rgba(124,58,237,0.25), inset 0 0 20px rgba(124,58,237,0.08) !important;
  font-weight: 600 !important;
}
div[data-testid="element-container"]:has(.esb-active) + div[data-testid="element-container"] button::before {
  content: '';
  position: absolute; left: 0; top: 15%;
  height: 70%; width: 3px;
  background: linear-gradient(180deg, var(--brand), var(--aurora-1));
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 8px var(--aurora-glow);
}

/* User card */
.esb-footer-divider {
  height: 1px;
  background: rgba(255,255,255,0.06);
  margin: 16px 14px 10px 14px;
}
.esb-user-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; margin-bottom: 8px; border-radius: 12px;
  background: rgba(124,58,237,0.06);
  border: 1px solid rgba(124,58,237,0.15);
}
.esb-user-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--aurora-1));
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: #FFFFFF; flex-shrink: 0;
  box-shadow: 0 0 12px var(--brand-glow);
}
.esb-user-name {
  font-size: 0.8rem; font-weight: 600; color: #FFFFFF;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.esb-user-meta { display: flex; align-items: center; gap: 5px; margin-top: 2px; }
.esb-online-dot {
  width: 5px; height: 5px; border-radius: 50%; background: var(--success);
  box-shadow: 0 0 6px var(--success);
  animation: dot-pulse 2.5s ease-in-out infinite;
}
@keyframes dot-pulse {
  0%,100% { box-shadow: 0 0 4px var(--success); }
  50% { box-shadow: 0 0 10px var(--success), 0 0 20px rgba(14,203,129,0.3); }
}
.esb-user-role { font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }

/* Logout button */
.esb-logout-marker { height: 0; width: 0; visibility: hidden; margin: 0; padding: 0; }
div[data-testid="element-container"]:has(.esb-logout-marker) + div[data-testid="element-container"] button {
  background: rgba(255,71,87,0.06) !important;
  border: 1px solid rgba(255,71,87,0.2) !important;
  color: #FF4757 !important;
  text-align: center !important; justify-content: center !important;
  transition: all var(--t-med) !important; font-size: 0.78rem !important;
}
div[data-testid="element-container"]:has(.esb-logout-marker) + div[data-testid="element-container"] button:hover {
  background: rgba(255,71,87,0.15) !important;
  border-color: rgba(255,71,87,0.5) !important;
  color: #FFFFFF !important; transform: none !important;
  box-shadow: 0 0 16px rgba(255,71,87,0.3) !important;
}

.esb-version {
  font-size: 0.58rem; color: rgba(255,255,255,0.12);
  text-align: center; margin: 10px 14px 18px 14px;
  letter-spacing: 0.06em; font-family: 'JetBrains Mono', monospace;
}

/* ══════════════════════════════════════════════════════════════
   PAGE HEADER — "Mission Control"
══════════════════════════════════════════════════════════════ */
.ds-page-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  position: relative;
}
.ds-page-header::after {
  content: '';
  position: absolute; bottom: 0; left: 0;
  width: 100%; height: 1px;
  background: linear-gradient(90deg, var(--brand) 0%, var(--aurora-1) 50%, transparent 100%);
  opacity: 0.5;
}
.ds-page-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.62rem; font-weight: 600;
  background: linear-gradient(135deg, var(--brand-light), var(--aurora-1));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 10px;
}
.ds-page-title {
  font-size: 2rem; font-weight: 800;
  letter-spacing: -0.04em; line-height: 1.15; margin-bottom: 10px;
  background: linear-gradient(135deg, #FFFFFF 0%, #C4B5FD 50%, var(--aurora-1) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.ds-page-subtitle {
  font-size: 0.9rem; color: var(--text-secondary);
  font-weight: 400; line-height: 1.65; max-width: 700px;
}

/* ══════════════════════════════════════════════════════════════
   CARDS — Glassmorphism Premium
══════════════════════════════════════════════════════════════ */
.ds-card {
  background: rgba(12,11,26,0.85);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.5rem;
  position: relative; overflow: hidden;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  transition: all var(--t-med);
}
.ds-card::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(124,58,237,0.04) 0%, rgba(29,211,176,0.02) 100%);
  opacity: 0; transition: opacity var(--t-med);
}
.ds-card:hover {
  border-color: rgba(124,58,237,0.4);
  box-shadow: 0 0 0 1px rgba(124,58,237,0.15), 0 16px 48px rgba(0,0,0,0.5), 0 0 32px rgba(124,58,237,0.1);
  transform: translateY(-3px);
}
.ds-card:hover::before { opacity: 1; }

/* Top accent bar that glows on hover */
.ds-card-accent {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--brand), var(--aurora-1), transparent);
  opacity: 0; transition: opacity var(--t-med);
}
.ds-card:hover .ds-card-accent { opacity: 1; }

/* KPI card variant */
.ds-kpi-card {
  background: rgba(10,9,22,0.9);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.4rem 1.6rem;
  position: relative; overflow: hidden;
  backdrop-filter: blur(20px);
  transition: all var(--t-med);
}
.ds-kpi-card:hover {
  border-color: rgba(124,58,237,0.35);
  box-shadow: 0 8px 32px rgba(124,58,237,0.12), 0 0 0 1px rgba(124,58,237,0.1);
  transform: translateY(-2px);
}
.ds-kpi-label {
  font-size: 0.68rem; font-weight: 600;
  color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;
  margin-bottom: 10px;
}
.ds-kpi-value {
  font-size: 2.1rem; font-weight: 800;
  color: var(--text-primary); letter-spacing: -0.04em; line-height: 1; margin-bottom: 6px;
}
.ds-kpi-delta { font-size: 0.72rem; font-weight: 600; color: var(--success); }
.ds-kpi-delta.negative { color: var(--danger); }

/* ══════════════════════════════════════════════════════════════
   BADGES — Neon-bordered pills
══════════════════════════════════════════════════════════════ */
.ds-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 11px; border-radius: 20px;
  font-size: 0.62rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.ds-badge-brand  { background: rgba(124,58,237,0.12); color: #C4B5FD; border: 1px solid rgba(124,58,237,0.35); }
.ds-badge-success{ background: rgba(14,203,129,0.1);  color: #34D399;  border: 1px solid rgba(14,203,129,0.3); }
.ds-badge-warning{ background: rgba(240,178,84,0.1);  color: #FCD34D;  border: 1px solid rgba(240,178,84,0.3); }
.ds-badge-danger { background: rgba(255,71,87,0.1);   color: #FF6B6B;  border: 1px solid rgba(255,71,87,0.3); }
.ds-badge-info   { background: rgba(0,210,255,0.1);   color: #00D2FF;  border: 1px solid rgba(0,210,255,0.3); }
.ds-badge-muted  { background: rgba(255,255,255,0.05);color: var(--text-secondary);border: 1px solid var(--border); }
.ds-badge-aurora { background: rgba(29,211,176,0.1);  color: #1DD3B0;  border: 1px solid rgba(29,211,176,0.35); }
.ds-badge-gold   { background: rgba(245,200,66,0.1);  color: #F5C842;  border: 1px solid rgba(245,200,66,0.35); }

/* Status dot */
.ds-status-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 5px;
}
.ds-status-dot.online  { background: var(--success); box-shadow: 0 0 8px var(--success-glow); animation: pulse-green 2.5s infinite; }
.ds-status-dot.offline { background: var(--danger); }
.ds-status-dot.warning { background: var(--warning); }
@keyframes pulse-green {
  0%,100% { box-shadow: 0 0 5px var(--success-glow); }
  50% { box-shadow: 0 0 14px rgba(14,203,129,0.8); }
}

/* ══════════════════════════════════════════════════════════════
   BUTTONS — Vivid gradient with glow
══════════════════════════════════════════════════════════════ */
.stButton > button {
  background: linear-gradient(135deg, #7C3AED 0%, #9B59E8 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.65rem 1.6rem !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em !important;
  transition: all var(--t-med) !important;
  box-shadow: 0 4px 14px rgba(124,58,237,0.4), 0 0 0 1px rgba(124,58,237,0.2) !important;
  position: relative !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #8B47FF 0%, #A969F5 100%) !important;
  box-shadow: 0 6px 24px rgba(124,58,237,0.55), 0 0 32px rgba(124,58,237,0.2) !important;
  transform: translateY(-2px) !important;
}
.stButton > button:active {
  transform: translateY(0px) !important;
  box-shadow: 0 2px 8px rgba(124,58,237,0.4) !important;
}

/* ══════════════════════════════════════════════════════════════
   INPUTS & FORMS — Dark glass with aurora focus
══════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div,
.stDateInput > div > div > input {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
  font-size: 0.875rem !important;
  transition: all var(--t-med) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
  border-color: rgba(124,58,237,0.7) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.18), 0 0 20px rgba(124,58,237,0.1) !important;
  background: rgba(124,58,237,0.06) !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color: rgba(168,164,192,0.4) !important; }

/* Field labels */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stTextArea label, .stDateInput label, .stSlider label,
.stRadio label, .stCheckbox label, .stFileUploader label {
  font-size: 0.72rem !important; font-weight: 600 !important;
  color: var(--text-muted) !important; text-transform: uppercase !important;
  letter-spacing: 0.09em !important; margin-bottom: 5px !important;
}

/* Slider — brand gradient track */
.stSlider > div > div > div > div {
  background: linear-gradient(90deg, var(--brand), var(--aurora-1)) !important;
}

/* ══════════════════════════════════════════════════════════════
   METRICS — st.metric with glow borders
══════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
  background: rgba(10,9,22,0.9) !important;
  border: 1px solid var(--border) !important;
  border-radius: 18px !important;
  padding: 1.2rem 1.4rem !important;
  transition: all var(--t-med) !important;
  backdrop-filter: blur(12px);
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(124,58,237,0.03), transparent);
  pointer-events: none;
}
[data-testid="stMetric"]:hover {
  border-color: rgba(124,58,237,0.35) !important;
  box-shadow: 0 6px 24px rgba(124,58,237,0.12) !important;
  transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
  font-size: 0.65rem !important; font-weight: 600 !important;
  color: var(--text-muted) !important; text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
  font-size: 1.7rem !important; font-weight: 800 !important;
  color: var(--text-primary) !important; letter-spacing: -0.04em !important;
}
[data-testid="stMetricDelta"] { font-size: 0.72rem !important; font-weight: 600 !important; }

/* ══════════════════════════════════════════════════════════════
   TABS — Glass pill tabs
══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 4px !important; gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-secondary) !important;
  font-size: 0.82rem !important; font-weight: 500 !important;
  padding: 8px 20px !important; border-radius: 10px !important;
  transition: all var(--t-med) !important; border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-primary) !important;
  background: rgba(255,255,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(124,58,237,0.3), rgba(29,211,176,0.15)) !important;
  color: #FFFFFF !important;
  box-shadow: 0 0 20px rgba(124,58,237,0.2), inset 0 1px 0 rgba(255,255,255,0.1) !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ══════════════════════════════════════════════════════════════
   EXPANDERS
══════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text-secondary) !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  transition: all var(--t-med) !important;
}
.streamlit-expanderHeader:hover {
  border-color: rgba(124,58,237,0.35) !important;
  background: rgba(124,58,237,0.06) !important; color: white !important;
}
.streamlit-expanderContent {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important; border-radius: 0 0 12px 12px !important;
}

/* ══════════════════════════════════════════════════════════════
   ALERTS
══════════════════════════════════════════════════════════════ */
.stSuccess {
  background: rgba(14,203,129,0.07) !important;
  border: 1px solid rgba(14,203,129,0.3) !important;
  border-radius: 12px !important; color: #34D399 !important;
}
.stWarning {
  background: rgba(240,178,84,0.07) !important;
  border: 1px solid rgba(240,178,84,0.3) !important;
  border-radius: 12px !important; color: #FCD34D !important;
}
.stError {
  background: rgba(255,71,87,0.07) !important;
  border: 1px solid rgba(255,71,87,0.3) !important;
  border-radius: 12px !important; color: #FF6B6B !important;
}
.stInfo {
  background: rgba(124,58,237,0.07) !important;
  border: 1px solid rgba(124,58,237,0.3) !important;
  border-radius: 12px !important; color: #C4B5FD !important;
}

/* ══════════════════════════════════════════════════════════════
   DATAFRAMES / TABLES
══════════════════════════════════════════════════════════════ */
.stDataFrame {
  border: 1px solid var(--border) !important;
  border-radius: 16px !important; overflow: hidden !important;
}
.stDataFrame th {
  background: rgba(124,58,237,0.1) !important;
  color: #C4B5FD !important;
  font-size: 0.68rem !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: 0.1em !important;
  padding: 12px 16px !important;
  border-bottom: 1px solid rgba(124,58,237,0.2) !important;
}
.stDataFrame td {
  color: var(--text-secondary) !important;
  font-size: 0.82rem !important; padding: 10px 16px !important;
  border-bottom: 1px solid rgba(255,255,255,0.03) !important;
}
.stDataFrame tr:hover td { background: rgba(124,58,237,0.06) !important; }

/* ══════════════════════════════════════════════════════════════
   FILE UPLOADER
══════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  background: rgba(255,255,255,0.02) !important;
  border: 2px dashed rgba(124,58,237,0.25) !important;
  border-radius: 16px !important;
  transition: all var(--t-med) !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: rgba(124,58,237,0.6) !important;
  background: rgba(124,58,237,0.06) !important;
  box-shadow: 0 0 24px rgba(124,58,237,0.1) !important;
}
[data-testid="stFileUploader"] section { background: transparent !important; }

/* ══════════════════════════════════════════════════════════════
   CODE BLOCKS
══════════════════════════════════════════════════════════════ */
.stCodeBlock, pre {
  background: rgba(0,0,0,0.4) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.8rem !important;
}

/* ══════════════════════════════════════════════════════════════
   SPINNERS & PROGRESS
══════════════════════════════════════════════════════════════ */
.stSpinner > div { border-top-color: var(--brand) !important; }
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--brand), var(--aurora-1)) !important;
  border-radius: 4px !important;
  box-shadow: 0 0 12px rgba(124,58,237,0.4);
}

/* ══════════════════════════════════════════════════════════════
   CHAT COMPONENTS — Premium bubble design
══════════════════════════════════════════════════════════════ */
.ds-chat-user { display: flex; justify-content: flex-end; margin: 16px 0; }
.ds-chat-user-bubble {
  background: linear-gradient(135deg, #7C3AED 0%, #5C14CC 100%);
  color: #FFFFFF; padding: 13px 18px;
  border-radius: 18px 18px 4px 18px;
  max-width: 72%; font-size: 0.87rem; line-height: 1.6;
  box-shadow: 0 4px 20px rgba(124,58,237,0.4), 0 0 0 1px rgba(124,58,237,0.2);
}
.ds-chat-ai { display: flex; justify-content: flex-start; margin: 16px 0; gap: 11px; align-items: flex-start; }
.ds-chat-ai-avatar {
  width: 34px; height: 34px; flex-shrink: 0; margin-top: 4px;
  background: linear-gradient(135deg, rgba(29,211,176,0.15), rgba(124,58,237,0.15));
  border: 1px solid rgba(29,211,176,0.3); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
  box-shadow: 0 0 12px rgba(29,211,176,0.2);
}
.ds-chat-ai-bubble {
  background: rgba(12,11,26,0.9);
  border: 1px solid rgba(29,211,176,0.15);
  color: var(--text-secondary); padding: 13px 18px;
  border-radius: 4px 18px 18px 18px;
  max-width: 72%; font-size: 0.87rem; line-height: 1.65;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.ds-chat-meta {
  font-size: 0.62rem; color: rgba(168,164,192,0.4);
  text-align: right; margin-top: 4px; padding-right: 6px;
  font-family: 'JetBrains Mono', monospace;
}
.ds-chat-empty {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 5rem 2rem; text-align: center;
  border: 2px dashed rgba(124,58,237,0.15);
  border-radius: 24px;
  background: rgba(124,58,237,0.02);
  backdrop-filter: blur(8px);
}
.ds-chat-empty-icon { font-size: 3rem; margin-bottom: 18px; filter: drop-shadow(0 0 20px rgba(124,58,237,0.4)); }
.ds-chat-empty-title { font-size: 1rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; }
.ds-chat-empty-sub { font-size: 0.82rem; color: var(--text-muted); }

/* ══════════════════════════════════════════════════════════════
   CITATION CARDS
══════════════════════════════════════════════════════════════ */
.ds-citation {
  background: rgba(29,211,176,0.04);
  border: 1px solid rgba(29,211,176,0.2);
  border-left: 3px solid var(--aurora-1);
  border-radius: 0 12px 12px 0;
  padding: 10px 16px; margin: 6px 0;
}
.ds-citation-title { font-size: 0.75rem; font-weight: 600; color: var(--aurora-1); margin-bottom: 4px; }
.ds-citation-excerpt { font-size: 0.72rem; color: var(--text-muted); font-style: italic; line-height: 1.45; }

/* ══════════════════════════════════════════════════════════════
   SHAP FEATURE ROWS
══════════════════════════════════════════════════════════════ */
.ds-feature-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px; margin: 5px 0;
  transition: all var(--t-fast);
}
.ds-feature-row:hover {
  background: rgba(124,58,237,0.07);
  border-color: rgba(124,58,237,0.25);
  transform: translateX(2px);
}
.ds-feature-name { color: var(--text-secondary); font-weight: 500; font-size: 0.82rem; }
.ds-feature-bar {
  flex: 1; height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px; margin: 0 14px; overflow: hidden;
}
.ds-feature-bar-fill {
  height: 100%; border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}
.ds-feature-value { font-weight: 700; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; }
.ds-feature-value.positive { color: var(--success); }
.ds-feature-value.negative { color: var(--danger); }

/* ══════════════════════════════════════════════════════════════
   RESULT HERO CARD — Premium underwriting reveal
══════════════════════════════════════════════════════════════ */
.ds-result-hero {
  background:
    radial-gradient(ellipse 60% 80% at 50% -10%, rgba(124,58,237,0.2) 0%, transparent 65%),
    linear-gradient(180deg, rgba(124,58,237,0.08) 0%, rgba(10,9,22,0.95) 100%);
  border: 1px solid rgba(124,58,237,0.35);
  border-radius: 24px;
  padding: 2.5rem 2rem; text-align: center;
  position: relative; overflow: hidden; margin: 1.5rem 0;
  backdrop-filter: blur(20px);
  box-shadow: 0 0 60px rgba(124,58,237,0.12), 0 24px 48px rgba(0,0,0,0.4);
}
.ds-result-hero::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--brand), var(--aurora-1), transparent);
}
.ds-result-label {
  font-size: 0.65rem; font-weight: 700; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 12px;
}
.ds-result-value {
  font-size: 3.4rem; font-weight: 900;
  letter-spacing: -0.05em; line-height: 1; margin-bottom: 8px;
  background: linear-gradient(135deg, #FFFFFF 0%, #C4B5FD 50%, var(--aurora-1) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  filter: drop-shadow(0 0 20px rgba(124,58,237,0.3));
}
.ds-result-sub { font-size: 0.82rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

/* ══════════════════════════════════════════════════════════════
   SECTION TITLES & DIVIDERS
══════════════════════════════════════════════════════════════ */
.ds-section-title {
  font-size: 0.65rem; font-weight: 700;
  background: linear-gradient(90deg, var(--brand-light), var(--aurora-1));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: uppercase; letter-spacing: 0.14em;
  margin-bottom: 14px; margin-top: 10px;
}
.ds-section-divider {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--brand-dim), var(--border), transparent);
  margin: 1.75rem 0;
}
hr {
  border: none !important; border-top: 1px solid var(--border) !important;
  margin: 2rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════
   MONITORING DASHBOARD
══════════════════════════════════════════════════════════════ */
.ds-monitor-gauge {
  background: rgba(10,9,22,0.9);
  border: 1px solid var(--border);
  border-radius: 16px; padding: 1.4rem; text-align: center;
  backdrop-filter: blur(12px);
  transition: all var(--t-med);
}
.ds-monitor-gauge:hover { border-color: rgba(124,58,237,0.35); }
.ds-monitor-gauge-label {
  font-size: 0.62rem; font-weight: 700; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px;
}
.ds-monitor-gauge-value {
  font-size: 2.2rem; font-weight: 900;
  letter-spacing: -0.04em; line-height: 1;
  background: linear-gradient(135deg, #FFFFFF, var(--aurora-1));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.ds-health-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: 10px; margin: 5px 0;
  transition: all var(--t-fast);
}
.ds-health-item:hover { border-color: rgba(124,58,237,0.25); background: rgba(124,58,237,0.05); }
.ds-health-name { font-size: 0.85rem; font-weight: 500; color: var(--text-secondary); }
.ds-log-viewer {
  background: rgba(0,0,0,0.5);
  border: 1px solid var(--border); border-radius: 12px; padding: 1rem;
  font-family: 'JetBrains Mono', monospace; font-size: 0.76rem;
  color: var(--text-muted); line-height: 1.7;
  max-height: 320px; overflow-y: auto;
}
.ds-log-viewer .log-error { color: var(--danger); }
.ds-log-viewer .log-warn { color: var(--warning); }
.ds-log-viewer .log-info { color: var(--text-muted); }
.ds-log-viewer .log-ok { color: var(--success); }

/* ══════════════════════════════════════════════════════════════
   AUTHENTICATION — Dramatic split-screen
══════════════════════════════════════════════════════════════ */
.ds-login-wrapper {
  min-height: 100vh;
  background: radial-gradient(ellipse 100% 80% at 20% 20%, rgba(124,58,237,0.15) 0%, transparent 55%),
              radial-gradient(ellipse 80% 60% at 80% 80%, rgba(29,211,176,0.08) 0%, transparent 50%),
              #03020A;
  display: flex; align-items: center; justify-content: center;
}
.ds-login-card {
  background: rgba(12,11,26,0.9);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 28px; padding: 2.5rem; width: 100%; max-width: 450px;
  box-shadow: 0 0 80px rgba(124,58,237,0.15), 0 24px 64px rgba(0,0,0,0.6),
              0 0 0 1px rgba(124,58,237,0.1);
  backdrop-filter: blur(32px);
}
.ds-demo-tag {
  display: flex; align-items: center; justify-content: space-between;
  padding: 11px 14px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border); border-radius: 12px; margin: 6px 0;
  cursor: default; transition: all var(--t-med);
}
.ds-demo-tag:hover {
  border-color: rgba(124,58,237,0.35);
  background: rgba(124,58,237,0.07);
}
.ds-demo-role { font-size: 0.82rem; font-weight: 600; color: var(--text-primary); }
.ds-demo-cred { font-size: 0.7rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

/* ══════════════════════════════════════════════════════════════
   HERO SECTION (Home Page) — Cinematic
══════════════════════════════════════════════════════════════ */
.ds-hero {
  background:
    radial-gradient(ellipse 80% 80% at 50% -20%, rgba(124,58,237,0.25) 0%, transparent 60%),
    radial-gradient(ellipse 50% 60% at 90% 50%, rgba(29,211,176,0.1) 0%, transparent 55%),
    linear-gradient(160deg, rgba(124,58,237,0.08) 0%, rgba(10,9,22,0.95) 100%);
  border: 1px solid rgba(124,58,237,0.25);
  border-radius: 28px; padding: 3.5rem 3rem;
  position: relative; overflow: hidden; margin-bottom: 2.5rem;
  backdrop-filter: blur(16px);
  box-shadow: 0 0 80px rgba(124,58,237,0.1), 0 24px 48px rgba(0,0,0,0.4);
}
.ds-hero::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--brand) 30%, var(--aurora-1) 70%, transparent 100%);
}
.ds-hero-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.65rem; font-weight: 700;
  background: linear-gradient(90deg, var(--brand-light), var(--aurora-1));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  text-transform: uppercase; letter-spacing: 0.16em; margin-bottom: 14px;
}
.ds-hero-title {
  font-size: 3.2rem; font-weight: 900; line-height: 1.1; letter-spacing: -0.04em;
  margin-bottom: 18px;
  background: linear-gradient(135deg, #FFFFFF 0%, #C4B5FD 45%, var(--aurora-1) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  filter: drop-shadow(0 0 30px rgba(124,58,237,0.2));
}
.ds-hero-sub {
  font-size: 1rem; color: var(--text-secondary); line-height: 1.7;
  max-width: 580px; margin-bottom: 0;
}
.ds-hero-orb {
  position: absolute; top: -80px; right: -80px;
  width: 360px; height: 360px;
  background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, rgba(29,211,176,0.08) 40%, transparent 70%);
  border-radius: 50%; pointer-events: none;
  animation: orb-pulse 8s ease-in-out infinite;
}
.ds-hero-orb-2 {
  position: absolute; bottom: -60px; right: 200px;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(29,211,176,0.1) 0%, transparent 70%);
  border-radius: 50%; pointer-events: none;
  animation: orb-pulse 12s ease-in-out infinite reverse;
}
@keyframes orb-pulse {
  0%,100% { transform: scale(1) rotate(0deg); opacity: 0.6; }
  50%      { transform: scale(1.12) rotate(6deg); opacity: 1; }
}

/* ══════════════════════════════════════════════════════════════
   MODULE STAT CHIPS
══════════════════════════════════════════════════════════════ */
.ds-stat-chip {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 6px 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px; font-size: 0.72rem; color: var(--text-secondary);
  font-weight: 500; transition: all var(--t-med);
}
.ds-stat-chip:hover {
  border-color: rgba(124,58,237,0.35);
  background: rgba(124,58,237,0.08);
  color: var(--text-primary);
}
.ds-stat-chip strong { color: #FFFFFF; }

/* ══════════════════════════════════════════════════════════════
   MODULE CARD — on Home page
══════════════════════════════════════════════════════════════ */
.ds-module-card {
  background: rgba(12,11,26,0.9);
  border: 1px solid var(--border); border-radius: 20px; padding: 1.6rem;
  position: relative; overflow: hidden;
  backdrop-filter: blur(20px); transition: all var(--t-med);
  cursor: default;
}
.ds-module-card-glow {
  position: absolute; top: -40px; right: -40px;
  width: 120px; height: 120px; border-radius: 50%;
  opacity: 0; transition: opacity var(--t-med); pointer-events: none;
}
.ds-module-card:hover { border-color: rgba(124,58,237,0.4); transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 0 32px rgba(124,58,237,0.12); }
.ds-module-card:hover .ds-module-card-glow { opacity: 1; }

/* ══════════════════════════════════════════════════════════════
   ARCHITECTURE GRID
══════════════════════════════════════════════════════════════ */
.ds-arch-grid {
  display: grid; grid-template-columns: repeat(4,1fr); gap: 1px;
  background: var(--border); border-radius: 16px; overflow: hidden;
}
.ds-arch-cell {
  background: rgba(12,11,26,0.95); padding: 1.4rem 1rem;
  text-align: center; transition: all var(--t-med);
}
.ds-arch-cell:hover { background: rgba(124,58,237,0.07); }
.ds-arch-layer-label {
  font-size: 0.58rem; font-weight: 700; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 8px;
}
.ds-arch-layer-value {
  font-size: 0.85rem; font-weight: 600;
  background: linear-gradient(135deg, var(--brand-light), var(--aurora-1));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}

/* ══════════════════════════════════════════════════════════════
   TYPOGRAPHY OVERRIDES
══════════════════════════════════════════════════════════════ */
h1 { color: var(--text-primary) !important; font-weight: 900 !important; letter-spacing: -0.04em !important; }
h2 { color: var(--text-primary) !important; font-weight: 800 !important; letter-spacing: -0.03em !important; }
h3, h4 { color: var(--text-primary) !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }

.stMarkdown p {
  color: var(--text-secondary); font-size: 0.9rem; line-height: 1.7;
}

/* Markdown tables */
.stMarkdown table { border-collapse: collapse; width: 100%; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.stMarkdown th {
  background: rgba(124,58,237,0.1); color: #C4B5FD;
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.1em; padding: 12px 16px;
  border-bottom: 1px solid rgba(124,58,237,0.2);
}
.stMarkdown td { color: var(--text-secondary); padding: 10px 16px; border-bottom: 1px solid rgba(255,255,255,0.03); }
.stMarkdown tr:hover td { background: rgba(124,58,237,0.05); }

/* ══════════════════════════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════════════════════════ */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position: 200% 0; }
}
@keyframes glow-pulse {
  0%,100% { box-shadow: 0 0 16px var(--brand-glow); }
  50%      { box-shadow: 0 0 32px var(--brand-glow), 0 0 60px rgba(124,58,237,0.1); }
}

/* Entry animations */
.ds-card, .ds-kpi-card, .ds-result-hero, [data-testid="stMetric"], .ds-module-card {
  animation: fade-up 0.35s ease both;
}

/* Stagger children */
.ds-card:nth-child(2) { animation-delay: 0.05s; }
.ds-card:nth-child(3) { animation-delay: 0.1s; }
.ds-card:nth-child(4) { animation-delay: 0.15s; }

/* Glow pulse on result hero */
.ds-result-hero { animation: fade-up 0.4s ease both, glow-pulse 4s ease-in-out 1s infinite; }

</style>
"""


def inject_design_system() -> None:
    """Injects the ACKO Ultra-Premium Midnight Aurora design system into Streamlit."""
    import streamlit as st
    st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)
