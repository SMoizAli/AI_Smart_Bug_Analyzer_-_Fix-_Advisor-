"""
theme_dark.py - Dark blue theme for the Bug Diagnosis app.

Usage (in app_test.py, right AFTER the original st.markdown(<style>...) block):

    from theme_dark import apply_dark_theme
    apply_dark_theme()

It injects CSS with !important so it overrides the light styles in app_test.py
without editing them. Pair it with .streamlit/config.toml (dark base theme)
so dataframes, JSON viewers and code blocks also turn dark.
"""
import streamlit as st

# ---- Palette (taken from your reference image) ----
BG          = "#0B1220"   # page background
BG_SOFT     = "#0F172A"   # sidebar / header
CARD        = "#111C33"   # cards / panels
CARD_HOVER  = "#16264A"
BORDER      = "#1E3A5F"
BLUE        = "#2563EB"   # primary
BLUE_DARK   = "#1D4ED8"
BLUE_LIGHT  = "#60A5FA"
TEXT        = "#E6EDF7"   # main text
TEXT_MUTED  = "#9FB0C8"   # captions
INPUT_BG    = "#0D1730"


def _sidebar_rules() -> str:
    base = 'html body [data-testid="stSidebar"] div[role="radiogroup"]'
    idle = []
    for n in range(1, 10):
        idle.append(f"{base} > label:nth-of-type({n})")
        idle.append(f"{base} > div:nth-child({n}) label")
    checked = [
        f"{base} > label:has(input:checked)",
        f"{base} > div label:has(input:checked)",
        f"{base} label:has(input:checked)",
    ]
    return f"""
{",".join(idle)} {{
    background: {CARD} !important;
    border: 2px solid {BORDER} !important;
}}
{",".join(idle)}:hover {{
    background: {CARD_HOVER} !important;
    border-color: {BLUE_LIGHT} !important;
}}
{",".join(checked)} {{
    background: linear-gradient(135deg, {BLUE} 0%, {BLUE_DARK} 100%) !important;
    border-color: {BLUE_LIGHT} !important;
    box-shadow: 0 6px 16px rgba(37,99,235,0.45) !important;
}}
{base} label p, {base} label span {{
    color: {TEXT} !important;
}}
{",".join(c + " p" for c in checked)}, {",".join(c + " span" for c in checked)} {{
    color: #FFFFFF !important;
}}
"""


_CSS = f"""
<style>
/* ---------- App shell ---------- */
html body .stApp {{ background-color: {BG} !important; color: {TEXT} !important; }}
header[data-testid="stHeader"], .stAppHeader {{
    background-color: {BG_SOFT} !important;
    border-bottom: 1px solid {BORDER} !important;
}}
header[data-testid="stHeader"] * {{ color: {TEXT} !important; }}
html body [data-testid="stSidebar"] {{
    background-color: {BG_SOFT} !important;
    border-right: 2px solid {BORDER} !important;
}}
html body [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
html body [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {{
    color: {TEXT} !important;
}}
.sidebar-bottom-anchor {{ border-top: 1px solid {BORDER} !important; }}

/* ---------- Make ALL text visible ---------- */
.stApp p:not([style]), .stApp span:not([style]), .stApp label,
.stApp li, .stApp h1, .stApp h2, .stApp h3:not([style]), .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMetricValue"], .stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stWidgetLabel"] p, .stApp summary, .stApp summary span {{
    color: {TEXT} !important;
}}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p,
.stApp small {{
    color: {TEXT_MUTED} !important;
}}
.stApp code {{
    color: {BLUE_LIGHT} !important;
    background-color: {INPUT_BG} !important;
}}
.stApp hr {{ border-color: {BORDER} !important; }}

/* ---------- Cards / containers ---------- */
html body [data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {CARD} !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.35) !important;
}}
html body [data-testid="stExpander"] {{
    background-color: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}

/* Dashboard metric tiles (inline-styled pastel cards in app_test.py) */
div[style*="border-radius: 22px"] {{
    background-color: {CARD} !important;
    border-color: {BORDER} !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.35) !important;
}}
div[style*="border-radius: 22px"] p {{ color: {TEXT_MUTED} !important; }}
div[style*="border-radius: 22px"] p:first-child {{ color: {BLUE_LIGHT} !important; }}
div[style*="border-radius: 22px"] h2 {{ color: #FFFFFF !important; }}

/* ---------- Buttons ---------- */
html body div.stButton > button {{
    background: linear-gradient(135deg, {BLUE} 0%, {BLUE_DARK} 100%) !important;
    border: 1px solid {BLUE_LIGHT} !important;
    color: #FFFFFF !important;
}}
html body div.stButton > button:hover {{
    background: linear-gradient(135deg, #3B82F6 0%, {BLUE} 100%) !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.5) !important;
}}
html body div.stButton > button p, html body div.stButton > button span {{
    color: #FFFFFF !important;
}}

/* ---------- Inputs ---------- */
html body .stTextArea textarea, html body .stTextInput input {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 2px solid {BORDER} !important;
    caret-color: {BLUE_LIGHT} !important;
}}
html body .stTextArea textarea::placeholder, html body .stTextInput input::placeholder {{
    color: {TEXT_MUTED} !important; opacity: 1 !important;
}}
html body .stTextArea textarea:focus, html body .stTextInput input:focus {{
    border-color: {BLUE_LIGHT} !important;
}}
html body div[data-baseweb="select"] {{
    background-color: {INPUT_BG} !important;
    border: 2px solid {BORDER} !important;
}}
html body div[data-baseweb="select"] * {{ color: {TEXT} !important; }}
div[data-baseweb="popover"], div[data-baseweb="popover"] ul,
div[data-baseweb="menu"], div[data-baseweb="popover"] > div {{
    background-color: {CARD} !important;
}}
div[data-baseweb="popover"] li, div[data-baseweb="popover"] li * {{
    background-color: {CARD} !important;
    color: {TEXT} !important;
}}
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] {{
    background-color: {CARD_HOVER} !important;
}}
html body [data-testid="stFileUploader"] section {{
    background-color: {INPUT_BG} !important;
    border: 2px dashed {BLUE} !important;
}}
html body [data-testid="stFileUploader"] section * {{ color: {TEXT} !important; }}
[data-testid="stFileUploader"] small {{ color: {TEXT_MUTED} !important; }}

/* ---------- Alerts (st.info / success / warning / error) ---------- */
html body div[data-testid="stAlert"] {{
    background-color: {CARD} !important;
    border: 2px solid {BLUE} !important;
}}
html body div[data-testid="stAlert"] * {{ color: {TEXT} !important; }}

/* ---------- Badges ---------- */
.stApp .badge-bug-id {{
    background-color: {INPUT_BG} !important; color: {BLUE_LIGHT} !important;
    border: 2px solid {BLUE} !important;
}}
.stApp .badge-filter-box {{
    background: #12305E !important; color: #BFDBFE !important;
    border: 1px solid {BLUE} !important;
}}
.stApp .badge-verified-kb {{
    background: #0F3D2A !important; color: #86EFAC !important; border: 1px solid #22C55E !important;
}}
.stApp .badge-unresolved {{
    background: #4C1620 !important; color: #FCA5A5 !important; border: 1px solid #EF4444 !important;
}}
.stApp .badge-pending {{
    background: #4A3510 !important; color: #FDE68A !important; border: 1px solid #F59E0B !important;
}}

/* ---------- Plotly charts (axis / legend / labels were dark or pink) ---------- */
.js-plotly-plot .xtick text, .js-plotly-plot .ytick text,
.js-plotly-plot .xtitle, .js-plotly-plot .ytitle,
.js-plotly-plot .gtitle, .js-plotly-plot .legendtext,
.js-plotly-plot .slicetext, .js-plotly-plot .textpoint text {{
    fill: {TEXT} !important;
}}
.js-plotly-plot .gridlayer path, .js-plotly-plot .xgrid, .js-plotly-plot .ygrid {{
    stroke: {BORDER} !important;
}}
.js-plotly-plot .xaxislayer-above path, .js-plotly-plot .yaxislayer-above path,
.js-plotly-plot .crisp {{ stroke: #3B5B8C !important; }}

/* ---------- Sidebar radio pills ---------- */
{_sidebar_rules()}
</style>
"""


def apply_dark_theme() -> None:
    """Inject the dark theme. Call after the app's original CSS block."""
    st.markdown(_CSS, unsafe_allow_html=True)
