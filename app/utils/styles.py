"""
Global CSS for the Summary dashboard.

Design language: light, modern, glassmorphism panels over a soft brand-tinted
gradient. Salasar brand palette:
    navy   #172962   deep blue #2d448d   lime #a6ce39   sky #459fda
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Typography ───────────────────────────────────────────────────────────── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] * {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ── App background: soft light gradient + blurred brand colour blobs ──────── */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(900px 620px at 10% 6%, rgba(166,206,57,0.20), transparent 60%),
        radial-gradient(900px 640px at 90% 10%, rgba(69,159,218,0.22), transparent 55%),
        radial-gradient(820px 720px at 72% 96%, rgba(45,68,141,0.14), transparent 60%),
        linear-gradient(135deg, #eef3fb 0%, #f6f9fd 45%, #eef5ee 100%) !important;
    background-attachment: fixed !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stMainBlockContainer"] {
    padding-top: 1.4rem !important;
    padding-bottom: 3rem !important;
    max-width: 1500px;
}

/* Hide default chrome for a cleaner dashboard */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* ── Hero header band (glass) ──────────────────────────────────────────────── */
.app-hero {
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; padding: 18px 26px; margin-bottom: 20px;
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.65);
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(23,41,98,0.10), inset 0 1px 0 rgba(255,255,255,0.6);
}
.hero-left { display: flex; align-items: center; gap: 18px; }
.hero-logo {
    height: 44px; width: auto; background: #fff; padding: 6px 10px;
    border-radius: 10px; box-shadow: 0 2px 8px rgba(23,41,98,0.12);
}
.hero-title {
    font-size: 22px; font-weight: 800; color: #172962;
    letter-spacing: -0.02em; line-height: 1.1;
}
.hero-sub { font-size: 12.5px; color: #5b6b90; font-weight: 500; margin-top: 3px; }
.hero-badge {
    background: linear-gradient(135deg, #a6ce39, #8db82f); color: #14310a;
    font-weight: 800; font-size: 13px; letter-spacing: 0.04em;
    padding: 9px 18px; border-radius: 999px;
    box-shadow: 0 4px 12px rgba(141,184,47,0.40); white-space: nowrap;
}

/* ── Tabs (pill style, glass) ──────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    gap: 8px !important;
    background: rgba(255,255,255,0.50) !important;
    backdrop-filter: blur(10px) saturate(150%);
    padding: 7px !important; border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.65) !important;
    box-shadow: 0 4px 16px rgba(23,41,98,0.07);
}
[data-baseweb="tab"] {
    height: auto !important; border-radius: 11px !important;
    padding: 9px 18px !important; color: #3a4a73 !important;
    font-weight: 600 !important; font-size: 13.5px !important;
    transition: all .15s ease !important; background: transparent !important;
}
[data-baseweb="tab"]:hover { background: rgba(45,68,141,0.07) !important; }
[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #2d448d 0%, #172962 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(45,68,141,0.35) !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* ── Glass section cards (st.container(border=True)) ───────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.58) !important;
    backdrop-filter: blur(16px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(160%) !important;
    border: 1px solid rgba(255,255,255,0.70) !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 34px rgba(23,41,98,0.10), inset 0 1px 0 rgba(255,255,255,0.6) !important;
    padding: 22px 24px !important;
    margin-bottom: 18px !important;
}

/* ── Section headings ──────────────────────────────────────────────────────── */
.section-label {
    font-size: 10.5px; font-weight: 800; letter-spacing: 0.14em;
    text-transform: uppercase; color: #5a8a16; margin: 0 0 3px 0;
}
.section-title {
    font-size: 18px; font-weight: 700; color: #172962; margin: 0 0 4px 0;
    letter-spacing: -0.01em;
}
.section-sub { font-size: 12.5px; color: #5b6b90; margin: 0 0 16px 0; line-height: 1.5; }
.totals-caption {
    font-size: 11px; font-weight: 700; letter-spacing: 0.10em;
    text-transform: uppercase; color: #5b6b90; margin: 18px 0 8px 0;
}

/* ── Data editor / dataframe ───────────────────────────────────────────────── */
[data-testid="stDataEditor"], [data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid rgba(45,68,141,0.14) !important;
    box-shadow: 0 4px 16px rgba(23,41,98,0.06) !important;
}

/* ── KPI metric cards ──────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.72) !important;
    border: 1px solid rgba(45,68,141,0.12) !important;
    border-radius: 16px !important; padding: 16px 18px !important;
    box-shadow: 0 6px 18px rgba(23,41,98,0.07) !important;
}
[data-testid="stMetricLabel"] p { color: #5b6b90 !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: #172962 !important; font-weight: 800 !important; }

/* ── Primary buttons (st.button) ───────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #2d448d 0%, #172962 100%) !important;
    color: #ffffff !important; border: none !important; border-radius: 11px !important;
    font-weight: 700 !important; font-size: 13.5px !important; padding: 10px 22px !important;
    box-shadow: 0 4px 14px rgba(45,68,141,0.30) !important;
    transition: transform .12s ease, box-shadow .12s ease, filter .12s ease !important;
}
[data-testid="stButton"] > button:hover {
    filter: brightness(1.08); transform: translateY(-1px);
    box-shadow: 0 7px 20px rgba(45,68,141,0.40) !important;
}

/* ── HTML grand-total tables (read-only, modern) ───────────────────────────── */
.table-scroll {
    overflow-x: auto; border-radius: 14px;
    border: 1px solid rgba(45,68,141,0.14);
    box-shadow: 0 4px 16px rgba(23,41,98,0.06); background: #ffffff;
}
.dash-table {
    width: 100%; border-collapse: collapse; font-size: 12.5px;
    font-family: inherit; white-space: nowrap;
}
.dash-table thead tr.main-header th {
    background: linear-gradient(135deg, #2d448d, #172962);
    color: #fff; font-weight: 700; padding: 11px 14px; text-align: center;
    font-size: 11.5px; letter-spacing: 0.04em; border-right: 1px solid rgba(255,255,255,0.10);
}
.dash-table thead tr.sub-header th {
    background: #233a7a; color: #c8d6f5; font-weight: 600; padding: 7px 12px;
    text-align: center; font-size: 10.5px; letter-spacing: 0.03em;
    border-right: 1px solid rgba(255,255,255,0.08);
}
.dash-table thead th:first-child { text-align: left; }
.dash-table tfoot tr td {
    background: #f3f7ff; color: #172962; font-weight: 700; padding: 11px 14px;
    text-align: right; border-top: 2px solid #a6ce39;
}
.dash-table tfoot tr td:first-child {
    text-align: left; color: #172962; font-weight: 800;
    position: sticky; left: 0; background: #eef3fc;
}

/* ── Alerts ────────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 12px !important; }
</style>
"""
