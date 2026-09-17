import streamlit as st
import pandas as pd
import json
import os
import sys
import datetime
import time
import textwrap

# Ensure src can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from pipeline import run_pipeline

# ------------------------------------------------------------------------------
# 1. SETUP & CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="MedGuard AI | Intelligent Follow-up System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to render HTML cleanly without markdown indentation code-block leaks
def render_html(html_str: str):
    """
    Renders custom HTML safely in Streamlit.
    Strips leading and trailing whitespace from every line and removes blank lines,
    ensuring Markdown never interprets any indented HTML line as a preformatted code block.
    """
    cleaned_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    cleaned_html = "\n".join(cleaned_lines)
    st.markdown(cleaned_html, unsafe_allow_html=True)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"
if "history" not in st.session_state:
    st.session_state.history = []
if "active_assessment" not in st.session_state:
    st.session_state.active_assessment = None

# ------------------------------------------------------------------------------
# 2. GLOBAL CSS STYLING (RAZORPAY-STYLE STARTUP POLISH, LIGHT SIDEBAR & CONTROLS)
# ------------------------------------------------------------------------------
render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background-color: #F8FAFC;
    color: #0F172A;
}

/* Hide Default Streamlit Chrome Elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}

/* -----------------------------------------------------------------------------
   PREMIUM LIGHT NAVIGATION SIDEBAR (RAZORPAY/STRIPE STYLE)
   ----------------------------------------------------------------------------- */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    bottom: 0 !important;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    height: 100vh !important;
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 4px 0 24px rgba(15, 23, 42, 0.03) !important;
    z-index: 999999 !important;
    transform: none !important;
    visibility: visible !important;
    display: block !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    overflow-y: auto !important;
}

section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div:first-child,
div[data-testid="stSidebarContent"],
div[data-testid="stSidebarUserContent"] {
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    padding: 1.5rem 1.15rem !important;
    background-color: #FFFFFF !important;
    box-sizing: border-box !important;
}

/* Hide Streamlit collapse toggle so sidebar is permanent */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Main Content Area Offset */
.main, [data-testid="stMain"] {
    margin-left: 280px !important;
    width: calc(100% - 280px) !important;
    box-sizing: border-box !important;
}

.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2.25rem !important;
    padding-right: 2.25rem !important;
    max-width: 1240px !important;
}

/* Sidebar Radio Navigation as Modern Nav Links */
[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.35rem !important;
    margin-top: 0.35rem !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    padding: 0.7rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #475569 !important;
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label p,
[data-testid="stSidebar"] div[role="radiogroup"] > label div,
[data-testid="stSidebar"] div[role="radiogroup"] > label span {
    color: #475569 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: #F1F5F9 !important;
    color: #0F172A !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover * {
    color: #0F172A !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked),
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) *,
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
    display: none !important;
}

/* Sidebar Logout Button */
[data-testid="stSidebar"] .stButton>button {
    background: #FFFFFF !important;
    color: #64748B !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
    height: auto !important;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background: #FEF2F2 !important;
    color: #EF4444 !important;
    border-color: #FECACA !important;
    transform: translateY(-1px) !important;
}

/* -----------------------------------------------------------------------------
   TOP FLOATING HEADER BAR
   ----------------------------------------------------------------------------- */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.85rem 1.5rem;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.top-header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.breadcrumb {
    font-size: 0.825rem;
    font-weight: 500;
    color: #64748B;
}
.breadcrumb span {
    color: #2563EB;
    font-weight: 700;
}
.page-title-heading {
    font-size: 1.2rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.02em;
    margin-top: 0.1rem;
}
.top-header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

/* Online Status Badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background-color: #F0FDF4;
    color: #15803D;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid #BBF7D0;
}
.status-dot {
    width: 7px;
    height: 7px;
    background-color: #22C55E;
    border-radius: 50%;
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.25);
}

.avatar-badge {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.825rem;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

/* -----------------------------------------------------------------------------
   CLEAN WHITE SAAS CARDS & HERO
   ----------------------------------------------------------------------------- */
.saas-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
    margin-bottom: 1.35rem;
}

.card-header-title {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-weight: 800;
    font-size: 1.15rem;
    color: #0F172A;
    margin-bottom: 0.2rem;
    letter-spacing: -0.01em;
}
.card-header-subtitle {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 1.15rem;
}

/* Sub-card Container for Individual Health Indicators */
.indicator-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.15rem 1.25rem;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
.indicator-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.08);
    border-color: #CBD5E1;
}
.indicator-box-title {
    font-weight: 700;
    font-size: 0.975rem;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0.25rem;
}
.indicator-box-desc {
    font-size: 0.8rem;
    color: #64748B;
    margin-bottom: 0.75rem;
    line-height: 1.4;
}

/* Metric Cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.35rem 1.5rem;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}
.metric-title {
    font-size: 0.725rem;
    font-weight: 800;
    color: #64748B;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.metric-subtitle {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 0.35rem;
    font-weight: 500;
}

/* -----------------------------------------------------------------------------
   MAIN CONTENT FORM CONTROLS (LIGHT THEME OVERRIDES)
   ----------------------------------------------------------------------------- */
.main label, .main [data-testid="stWidgetLabel"] p {
    color: #0F172A !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.35rem !important;
}

.main [data-baseweb="input"],
.main [data-baseweb="base-input"],
.main [data-baseweb="select"],
.main [data-baseweb="select"] > div,
.main .stSelectbox > div > div,
.main .stNumberInput > div > div,
.main .stTextInput > div > div,
.main .stDateInput > div > div {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    color: #0F172A !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
}

.main [data-baseweb="input"] input,
.main [data-baseweb="base-input"] input,
.main .stNumberInput input,
.main .stTextInput input,
.main .stDateInput input {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border: none !important;
}

.main [data-baseweb="select"] span,
.main [data-baseweb="select"] div {
    color: #0F172A !important;
    font-weight: 600 !important;
}

.main [data-baseweb="select"] svg,
.main .stDateInput svg {
    fill: #2563EB !important;
    color: #2563EB !important;
}

/* NumberInput Stepper Buttons (+ / -) */
.main .stNumberInput button,
.main [data-testid="stNumberInputStepDown"],
.main [data-testid="stNumberInputStepUp"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

.main .stNumberInput button:hover,
.main [data-testid="stNumberInputStepDown"]:hover,
.main [data-testid="stNumberInputStepUp"]:hover {
    background-color: #EFF6FF !important;
    background: #EFF6FF !important;
    color: #2563EB !important;
    border-color: #2563EB !important;
}

.main .stNumberInput button svg,
.main [data-testid="stNumberInputStepDown"] svg,
.main [data-testid="stNumberInputStepUp"] svg {
    fill: #0F172A !important;
}

.main .stNumberInput button:hover svg,
.main [data-testid="stNumberInputStepDown"]:hover svg,
.main [data-testid="stNumberInputStepUp"]:hover svg {
    fill: #2563EB !important;
}

/* Focus States */
.main [data-baseweb="input"]:focus-within,
.main [data-baseweb="select"]:focus-within,
.main .stSelectbox > div > div:focus-within,
.main .stNumberInput > div > div:focus-within,
.main .stDateInput > div > div:focus-within {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}

/* Popover Dropdown Menus & Calendars */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[data-baseweb="menu"],
div[data-baseweb="calendar"] {
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1) !important;
    color: #0F172A !important;
}

li[data-baseweb="menu-item"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
}

li[data-baseweb="menu-item"]:hover,
li[data-baseweb="menu-item"][aria-selected="true"] {
    background: #EFF6FF !important;
    color: #2563EB !important;
    font-weight: 700 !important;
}

/* -----------------------------------------------------------------------------
   SEGMENTED CONTROLS (YES / NO PILLS, ZERO BLACK DOTS)
   ----------------------------------------------------------------------------- */
.main div[role="radiogroup"] {
    display: flex !important;
    gap: 0.5rem !important;
    margin-top: 0.35rem !important;
    background: transparent !important;
}

.main div[role="radiogroup"] > label {
    flex: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #FFFFFF !important;
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
    padding: 0.55rem 0.85rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    margin: 0 !important;
    text-align: center !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}

.main div[role="radiogroup"] > label p,
.main div[role="radiogroup"] > label div,
.main div[role="radiogroup"] > label span {
    color: #0F172A !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    margin: 0 !important;
}

.main div[role="radiogroup"] > label:hover {
    background-color: #EFF6FF !important;
    background: #EFF6FF !important;
    border-color: #2563EB !important;
}

.main div[role="radiogroup"] > label:hover p,
.main div[role="radiogroup"] > label:hover div,
.main div[role="radiogroup"] > label:hover span {
    color: #1D4ED8 !important;
}

/* Hide native radio circles in main area */
.main div[role="radiogroup"] input[type="radio"],
.main div[role="radiogroup"] input[type="radio"] + div,
.main [data-baseweb="radio"] input,
.main [data-baseweb="radio"] div:first-child {
    display: none !important;
}

/* Active Selected Pill: Blue/Purple gradient with white text */
.main div[role="radiogroup"] > label:has(input:checked),
.main div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

.main div[role="radiogroup"] > label:has(input:checked) p,
.main div[role="radiogroup"] > label:has(input:checked) div,
.main div[role="radiogroup"] > label:has(input:checked) span,
.main div[role="radiogroup"] > label[data-checked="true"] p,
.main div[role="radiogroup"] > label[data-checked="true"] div,
.main div[role="radiogroup"] > label[data-checked="true"] span {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* -----------------------------------------------------------------------------
   PRIMARY ACTION GRADIENT BUTTON
   ----------------------------------------------------------------------------- */
.main .stButton>button,
.stFormSubmitButton>button {
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-radius: 14px !important;
    height: 56px !important;
    padding: 0.75rem 2rem !important;
    border: none !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
    width: 100% !important;
}
.main .stButton>button:hover,
.stFormSubmitButton>button:hover {
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-2px) !important;
    color: #FFFFFF !important;
}

/* Disclaimer Card */
.disclaimer-card {
    background: #FFFFFF;
    border-left: 4px solid #2563EB;
    border-top: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
    border-radius: 0 12px 12px 0;
    padding: 1.15rem 1.35rem;
    margin-top: 2rem;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.55;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
}

/* Step Indicator Badges */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 1rem;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #475569;
}
.step-badge.active {
    background: #EFF6FF;
    border-color: #BFDBFE;
    color: #1D4ED8;
}

/* Footer */
.saas-footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    margin-top: 3rem;
    border-top: 1px solid #E2E8F0;
    color: #94A3B8;
    font-size: 0.825rem;
}
</style>
""")


# Load neighbourhoods dynamically from schema
@st.cache_data
def load_neighbourhoods():
    try:
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "medguard_feature_schema.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        features = schema.get("features", [])
        nhoods = [f.split("Neighbourhood_")[1] for f in features if f.startswith("Neighbourhood_")]
        return sorted(nhoods)
    except Exception:
        return ["JARDIM DA PENHA", "MATA DA PRAIA", "CENTRO", "ITARARÉ", "TABUAZEIRO", "ANDORINHAS", "BONFIM"]

neighbourhood_list = load_neighbourhoods()


# ------------------------------------------------------------------------------
# SCREEN 1: LOGIN SCREEN (SIDEBAR COMPLETELY HIDDEN & CONTENT CENTERED)
# ------------------------------------------------------------------------------
def render_login_screen():
    render_html("""
    <style>
    section[data-testid="stSidebar"], [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .main, [data-testid="stMain"] { margin-left: 0 !important; width: 100% !important; }
    </style>
    """)
    
    render_html("<div style='height: 40px;'></div>")
    
    col_left, col_mid, col_right = st.columns([1, 6, 1])
    
    with col_mid:
        panel_col1, panel_col2 = st.columns([5, 5], gap="large")
        
        with panel_col1:
            render_html("""
            <div style="background: linear-gradient(135deg, #0D1527 0%, #1E293B 100%); padding: 3.25rem 2.5rem; border-radius: 20px; color: #FFFFFF; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 12px 30px -5px rgba(13, 21, 39, 0.35);">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                        <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);">
                            🩺
                        </div>
                        <div>
                            <div style="font-weight: 800; font-size: 1.35rem; color: #FFFFFF; letter-spacing: -0.02em;">MedGuard AI</div>
                            <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 500;">Clinical Operations Platform</div>
                        </div>
                    </div>
                    
                    <div style="display: inline-block; padding: 0.3rem 0.85rem; background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 9999px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 1.25rem;">
                        AI-POWERED HEALTHCARE OPERATIONS
                    </div>
                    <h2 style="color: #FFFFFF; font-size: 1.95rem; font-weight: 800; line-height: 1.25; margin-bottom: 0.85rem; letter-spacing: -0.03em;">
                        Smarter patient follow-up. Better outcomes.
                    </h2>
                    <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.6; margin-bottom: 2rem;">
                        Intelligent clinical operations platform combining machine-learning attendance prediction with documented vulnerability prioritization.
                    </p>
                </div>
                
                <div style="border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; font-size: 0.875rem; color: #CBD5E1;">
                        <span style="color: #60A5FA; font-weight: bold;">✓</span> 103-Signal Calibrated Prediction Engine
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; font-size: 0.875rem; color: #CBD5E1;">
                        <span style="color: #60A5FA; font-weight: bold;">✓</span> Vulnerability-Aware Multi-Tier Matrix
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.75rem; font-size: 0.875rem; color: #CBD5E1;">
                        <span style="color: #60A5FA; font-weight: bold;">✓</span> Proactive Operational Outreach Protocols
                    </div>
                </div>
            </div>
            """)
            
        with panel_col2:
            render_html("""
            <div style="background: #FFFFFF; padding: 2.75rem 2.5rem; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);">
                <h3 style="color: #0F172A; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.35rem; letter-spacing: -0.02em;">Welcome back</h3>
                <p style="color: #64748B; font-size: 0.875rem; margin-bottom: 1.75rem;">Sign in to access the patient risk assessment platform.</p>
            </div>
            """)
            
            with st.form("login_form", border=False):
                username = st.text_input("Username / Email", value="", placeholder="admin")
                password = st.text_input("Password", value="", type="password", placeholder="••••••••••••")
                
                render_html("<div style='height: 12px;'></div>")
                login_submitted = st.form_submit_button("Sign In →", use_container_width=True)
                
                if login_submitted:
                    clean_user = username.strip()
                    clean_pass = password.strip()
                    if not clean_user or not clean_pass:
                        st.error("Invalid credentials. Please verify your username and password.")
                    elif clean_user == "admin" and clean_pass == "medguard2026":
                        st.session_state.authenticated = True
                        st.session_state.current_page = "Overview"
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your username and password.")
            
            render_html("""
            <div style="margin-top: 1.75rem; padding-top: 1.25rem; border-top: 1px solid #F1F5F9; text-align: center;">
                <span style="font-size: 0.775rem; color: #94A3B8; font-weight: 500;">
                    🔒 Secure clinical operations decision support platform
                </span>
            </div>
            """)
            
    render_html("""
    <div style="max-width: 820px; margin: 3rem auto 1rem auto;">
        <div class="disclaimer-card">
            <strong>System Notice:</strong> This system provides operational risk and follow-up prioritization based on appointment attendance patterns and documented vulnerability indicators. It is NOT a medical diagnosis, disease-severity score, or emergency-triage system.
        </div>
    </div>
    """)


# ------------------------------------------------------------------------------
# TOP FLOATING HEADER BAR
# ------------------------------------------------------------------------------
def render_top_header(page_title: str):
    render_html(f"""
    <div class="top-header">
        <div class="top-header-left">
            <div>
                <div class="breadcrumb">Home &nbsp;/&nbsp; <span>{page_title}</span></div>
                <div class="page-title-heading">{page_title}</div>
            </div>
        </div>
        <div class="top-header-right">
            <div class="status-badge">
                <span class="status-dot"></span> System Online
            </div>
            <div style="font-size: 1.15rem; color: #64748B; cursor: pointer; padding: 0.35rem; border-radius: 8px; background: #F8FAFC; border: 1px solid #E2E8F0;">🔔</div>
            <div class="avatar-badge">A</div>
        </div>
    </div>
    """)


# ------------------------------------------------------------------------------
# SCREEN 2: PROFESSIONAL LIGHT LEFT SIDEBAR
# ------------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        # 1. Branding Header
        render_html("""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.25rem 0 1.25rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1.15rem;">
            <div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); display: flex; align-items: center; justify-content: center; font-size: 1.4rem; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);">
                🩺
            </div>
            <div>
                <div style="font-weight: 800; font-size: 1.2rem; color: #0F172A; letter-spacing: -0.02em;">MedGuard AI</div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">Clinical Operations Platform</div>
            </div>
        </div>
        <div style="font-size: 0.68rem; font-weight: 800; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin: 0.5rem 0 0.35rem 0.5rem;">
            MAIN
        </div>
        """)
        
        # 2. Modern Navigation Links
        pages = ["Overview", "Patient Assessment", "Assessment History", "Analytics", "About"]
        icons = {
            "Overview": "🏠  Overview",
            "Patient Assessment": "👤  Patient Assessment",
            "Assessment History": "📋  Assessment History",
            "Analytics": "📊  Analytics",
            "About": "ℹ️  About"
        }
        
        display_options = [icons[p] for p in pages]
        current_display = icons.get(st.session_state.current_page, "🏠  Overview")
        current_idx = display_options.index(current_display)
        
        selected_display = st.radio(
            "Navigation Menu",
            display_options,
            index=current_idx,
            label_visibility="collapsed"
        )
        
        # Map back to simple page name and handle page changes
        selected_page = [p for p in pages if icons[p] == selected_display][0]
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()
            
        render_html("<div style='height: 80px;'></div>")
        
        # 3. System Status Card & Profile Footer
        render_html("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 14px; padding: 0.9rem; margin-bottom: 1rem;">
            <div style="font-size: 0.68rem; font-weight: 800; color: #64748B; letter-spacing: 0.06em; margin-bottom: 0.4rem; text-transform: uppercase;">SYSTEM STATUS</div>
            <div style="display: flex; align-items: center; gap: 0.45rem; font-size: 0.825rem; font-weight: 700; color: #15803D;">
                <span style="width: 8px; height: 8px; background-color: #22C55E; border-radius: 50%; box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.25);"></span> System Online
            </div>
            <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 0.2rem;">All models operational</div>
        </div>
        
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 0.25rem 0.5rem 0.25rem; border-top: 1px solid #E2E8F0; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.825rem; font-weight: bold;">A</div>
                <div>
                    <div style="font-size: 0.85rem; font-weight: 800; color: #0F172A;">Admin</div>
                    <div style="font-size: 0.7rem; color: #64748B; font-weight: 500;">Clinical Operations</div>
                </div>
            </div>
        </div>
        """)
        
        # 4. Logout Button
        if st.button("Logout", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.active_assessment = None
            st.session_state.current_page = "Overview"
            st.rerun()


# ------------------------------------------------------------------------------
# SCREEN 3: OVERVIEW SAAS LANDING DASHBOARD
# ------------------------------------------------------------------------------
def render_overview_screen():
    render_top_header("Overview")
    
    # 1. Startup Hero Section
    render_html("""
    <div style="background: linear-gradient(135deg, #0D1527 0%, #1E293B 100%); border-radius: 20px; padding: 3rem 2.5rem; color: #FFFFFF; position: relative; overflow: hidden; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);">
        <div style="position: absolute; right: -50px; top: -50px; width: 350px; height: 350px; background: radial-gradient(circle, rgba(37,99,235,0.25) 0%, rgba(124,58,237,0.05) 70%, transparent 100%); border-radius: 50%; filter: blur(40px);"></div>
        
        <div style="position: relative; z-index: 2; max-width: 780px;">
            <div style="display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.35rem 0.85rem; background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 9999px; font-size: 0.725rem; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 1.25rem;">
                <span>✦</span> AI-POWERED HEALTHCARE OPERATIONS
            </div>
            <h1 style="color: #FFFFFF; font-size: 2.35rem; font-weight: 800; line-height: 1.2; margin-bottom: 1rem; letter-spacing: -0.03em;">
                Smarter patient follow-up.<br/>Better healthcare outcomes.
            </h1>
            <p style="color: #94A3B8; font-size: 1.05rem; line-height: 1.6; margin-bottom: 2rem; max-width: 650px;">
                MedGuard AI helps healthcare teams identify appointment attendance risk and prioritize follow-up using calibrated machine learning and documented vulnerability indicators.
            </p>
        </div>
        
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; position: relative; z-index: 2;">
            <div style="padding: 0.75rem 1.25rem; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; font-size: 0.85rem; color: #CBD5E1; display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #60A5FA; font-weight: bold;">●</span> 103 Clinical Features
            </div>
            <div style="padding: 0.75rem 1.25rem; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; font-size: 0.85rem; color: #CBD5E1; display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #60A5FA; font-weight: bold;">●</span> 55.0% Calibrated Threshold
            </div>
            <div style="padding: 0.75rem 1.25rem; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; font-size: 0.85rem; color: #CBD5E1; display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: #60A5FA; font-weight: bold;">●</span> 2D Priority Action Matrix
            </div>
        </div>
    </div>
    """)
    
    # 2. Four Executive KPI Cards
    history = st.session_state.history
    total_assessments = len(history)
    high_risk_count = sum(1 for x in history if x.get("risk") == "High")
    highest_prio_count = sum(1 for x in history if x.get("priority") == "Highest")
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_html(f"""
        <div class="metric-card">
            <div style="font-size: 1.35rem; margin-bottom: 0.25rem;">📋</div>
            <div class="metric-title">TOTAL ASSESSMENTS</div>
            <div class="metric-value">{total_assessments}</div>
            <div class="metric-subtitle">Evaluated in current session</div>
        </div>
        """)
    with k2:
        render_html(f"""
        <div class="metric-card">
            <div style="font-size: 1.35rem; margin-bottom: 0.25rem;">⚠️</div>
            <div class="metric-title">HIGH-RISK PATIENTS</div>
            <div class="metric-value" style="color: #EF4444;">{high_risk_count}</div>
            <div class="metric-subtitle">Probability ≥ 55.0%</div>
        </div>
        """)
    with k3:
        render_html(f"""
        <div class="metric-card">
            <div style="font-size: 1.35rem; margin-bottom: 0.25rem;">🚨</div>
            <div class="metric-title">HIGHEST PRIORITY</div>
            <div class="metric-value" style="color: #B91C1C;">{highest_prio_count}</div>
            <div class="metric-subtitle">Urgent operational outreach</div>
        </div>
        """)
    with k4:
        render_html(f"""
        <div class="metric-card">
            <div style="font-size: 1.35rem; margin-bottom: 0.25rem;">🟢</div>
            <div class="metric-title">SYSTEM STATUS</div>
            <div class="metric-value" style="color: #15803D; font-size: 1.45rem;">ONLINE</div>
            <div class="metric-subtitle">All ML models operational</div>
        </div>
        """)
        
    render_html("<div style='height: 20px;'></div>")
    
    # 3. Action Panels
    c1, c2 = st.columns([6, 6])
    with c1:
        with st.container(border=True):
            render_html("""
            <div style="padding: 0.5rem 0;">
                <div style="display: inline-block; padding: 0.2rem 0.65rem; background: #EEF2FF; color: #4F46E5; border-radius: 6px; font-size: 0.72rem; font-weight: 800; margin-bottom: 0.75rem;">
                    WORKFLOW ENGINE
                </div>
                <h3 style="color: #0F172A; font-weight: 800; font-size: 1.4rem; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                    Start Patient Assessment
                </h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.35rem;">
                    Evaluate appointment attendance probability against calibrated 55% threshold and prioritize operational outreach according to documented vulnerability indicators.
                </p>
            </div>
            """)
            if st.button("✦  Start Assessment  →", key="ov_goto_assessment", use_container_width=True):
                st.session_state.current_page = "Patient Assessment"
                st.rerun()
                
    with c2:
        with st.container(border=True):
            render_html("""
            <div style="padding: 0.5rem 0;">
                <div style="display: inline-block; padding: 0.2rem 0.65rem; background: #F1F5F9; color: #475569; border-radius: 6px; font-size: 0.72rem; font-weight: 800; margin-bottom: 0.75rem;">
                    SESSION TELEMETRY
                </div>
                <h3 style="color: #0F172A; font-weight: 800; font-size: 1.4rem; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                    Live Operations Stream
                </h3>
            </div>
            """)
            if total_assessments == 0:
                render_html("""
                <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5; padding: 0.5rem 0 1.25rem 0;">
                    No assessments recorded in this session yet. Run a patient assessment to begin tracking live operational telemetry.
                </p>
                """)
            else:
                last_items = history[-3:][::-1]
                for item in last_items:
                    prio_color = {"Low": "#10B981", "Moderate": "#F59E0B", "High": "#EF4444", "Highest": "#B91C1C"}.get(item.get("priority"), "#64748B")
                    render_html(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #F1F5F9; font-size: 0.85rem;">
                        <span style="font-weight: 700; color: #0F172A;">{item.get('id')}</span>
                        <span style="color: #64748B;">{item.get('probability')*100:.1f}% risk</span>
                        <span style="font-weight: 800; color: {prio_color};">{item.get('priority')} Priority</span>
                        <span style="color: #94A3B8; font-size: 0.75rem;">{item.get('time')}</span>
                    </div>
                    """)

    # 4. How MedGuard AI Works Section
    render_html("<div style='height: 15px;'></div>")
    with st.container(border=True):
        render_html("""
        <div style="padding: 0.5rem 0 0.25rem 0;">
            <div style="display: inline-block; padding: 0.2rem 0.65rem; background: #EFF6FF; color: #1D4ED8; border-radius: 6px; font-size: 0.72rem; font-weight: 800; margin-bottom: 0.5rem;">
                PRODUCT ARCHITECTURE
            </div>
            <h3 style="color: #0F172A; font-weight: 800; font-size: 1.35rem; margin-bottom: 1.5rem; letter-spacing: -0.02em;">
                How MedGuard AI Works
            </h3>
        </div>
        """)
        
        hw1, hw2, hw3 = st.columns(3)
        with hw1:
            render_html("""
            <div style="padding: 1.35rem; background: #F8FAFC; border-radius: 14px; border: 1px solid #E2E8F0; height: 100%;">
                <div style="color: #2563EB; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.35rem;">01</div>
                <div style="font-weight: 800; color: #0F172A; font-size: 1rem; margin-bottom: 0.4rem;">Patient Data</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">Collect appointment parameters and documented clinical vulnerability indicators via verified schema.</div>
            </div>
            """)
        with hw2:
            render_html("""
            <div style="padding: 1.35rem; background: #F8FAFC; border-radius: 14px; border: 1px solid #E2E8F0; height: 100%;">
                <div style="color: #2563EB; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.35rem;">02</div>
                <div style="font-weight: 800; color: #0F172A; font-size: 1rem; margin-bottom: 0.4rem;">AI Assessment</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">XGBoost model evaluates attendance probability calibrated against 55.0% operating threshold.</div>
            </div>
            """)
        with hw3:
            render_html("""
            <div style="padding: 1.35rem; background: #F8FAFC; border-radius: 14px; border: 1px solid #E2E8F0; height: 100%;">
                <div style="color: #2563EB; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.35rem;">03</div>
                <div style="font-weight: 800; color: #0F172A; font-size: 1rem; margin-bottom: 0.4rem;">Follow-up Priority</div>
                <div style="color: #64748B; font-size: 0.85rem; line-height: 1.5;">Operational risk and vulnerability indicators are mapped to actionable follow-up protocols.</div>
            </div>
            """)

    # Safety Disclaimer
    render_html("""
    <div class="disclaimer-card">
        <strong>System Notice:</strong> This system provides operational risk and follow-up prioritization based on appointment attendance patterns and documented vulnerability indicators. It is NOT a medical diagnosis, disease-severity score, or emergency-triage system.
    </div>
    """)


# ------------------------------------------------------------------------------
# SCREEN 4 & 5: PATIENT ASSESSMENT WORKFLOW & RESULTS
# ------------------------------------------------------------------------------
def render_assessment_screen():
    render_top_header("Patient Assessment")
    
    # 1. Product Header & Step Indicator
    render_html("""
    <div class="saas-card" style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 2rem;">
        <div>
            <div style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.75rem; background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; margin-bottom: 0.5rem;">
                <span style="width: 6px; height: 6px; background: #22C55E; border-radius: 50%;"></span> AI ENGINE READY
            </div>
            <h2 style="color: #0F172A; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.02em; margin: 0 0 0.25rem 0;">
                Patient Risk Assessment
            </h2>
            <p style="color: #64748B; font-size: 0.875rem; margin: 0; max-width: 620px;">
                Evaluate appointment attendance risk and operational follow-up priority using documented clinical signals.
            </p>
        </div>
        <div style="font-size: 2.75rem; opacity: 0.9;">
            📋
        </div>
    </div>
    
    <div style="display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <span class="step-badge active">01 Patient Profile</span>
        <span class="step-badge active">02 Health Indicators</span>
        <span class="step-badge active">03 Appointment</span>
        <span class="step-badge active">04 Assessment</span>
    </div>
    """)
    
    with st.form("patient_assessment_form", border=False):
        # 1. PATIENT PROFILE CARD
        render_html("""
        <div class="saas-card">
            <div class="card-header-title">
                <span>👤</span> Patient Profile
            </div>
            <div class="card-header-subtitle">Basic demographic and socio-economic information</div>
        """)
        
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            gender = st.selectbox("Gender", options=["Female", "Male"], index=0)
        with p2:
            age = st.number_input("Age (years)", min_value=-1, max_value=120, value=40, step=1)
        with p3:
            neighbourhood = st.selectbox("Neighbourhood", options=neighbourhood_list)
        with p4:
            render_html("""
            <div class="indicator-box-title" style="margin-bottom: 0.1rem;">Scholarship</div>
            <div class="indicator-box-desc" style="margin-bottom: 0.2rem;">Bolsa Família welfare?</div>
            """)
            scholarship = st.radio("Scholarship", options=["Yes", "No"], index=1, horizontal=True, label_visibility="collapsed")
            
        render_html("</div>") # End patient profile card
        
        # 2. HEALTH INDICATORS CARD (4 INDIVIDUAL CLEAN SUB-CARDS)
        render_html("""
        <div class="saas-card">
            <div class="card-header-title">
                <span>❤️</span> Health Indicators
            </div>
            <div class="card-header-subtitle">Documented clinical conditions and vulnerability markers</div>
        """)
        
        h1, h2, h3, h4 = st.columns(4)
        with h1:
            render_html("""
            <div class="indicator-box">
                <div>
                    <div class="indicator-box-title"><span style="color: #EF4444;">♥</span> Hypertension</div>
                    <div class="indicator-box-desc">Does the patient have hypertension?</div>
                </div>
            """)
            hypertension = st.radio("Hypertension", options=["Yes", "No"], index=1, horizontal=True, label_visibility="collapsed")
            render_html("</div>")
            
        with h2:
            render_html("""
            <div class="indicator-box">
                <div>
                    <div class="indicator-box-title"><span style="color: #2563EB;">●</span> Diabetes</div>
                    <div class="indicator-box-desc">Does the patient have diabetes?</div>
                </div>
            """)
            diabetes = st.radio("Diabetes", options=["Yes", "No"], index=1, horizontal=True, label_visibility="collapsed")
            render_html("</div>")
            
        with h3:
            render_html("""
            <div class="indicator-box">
                <div>
                    <div class="indicator-box-title"><span style="color: #7C3AED;">🍷</span> Alcoholism</div>
                    <div class="indicator-box-desc">Documented alcohol dependency?</div>
                </div>
            """)
            alcoholism = st.radio("Alcoholism", options=["Yes", "No"], index=1, horizontal=True, label_visibility="collapsed")
            render_html("</div>")
            
        with h4:
            render_html("""
            <div class="indicator-box">
                <div>
                    <div class="indicator-box-title"><span style="color: #64748B;">♿</span> Handicap</div>
                    <div class="indicator-box-desc">Documented handicap level</div>
                </div>
            """)
            handicap_options = ["0 — None", "1 — Level 1", "2 — Level 2", "3 — Level 3", "4 — Level 4"]
            handicap_selected = st.selectbox("Handicap", options=handicap_options, index=0, label_visibility="collapsed")
            render_html("</div>")
            
        render_html("</div>") # End health indicators card
        
        # 3. APPOINTMENT INFORMATION CARD
        render_html("""
        <div class="saas-card">
            <div class="card-header-title">
                <span>▣</span> Appointment Information
            </div>
            <div class="card-header-subtitle">Appointment scheduling and communication details</div>
        """)
        
        a1, a2, a3 = st.columns(3)
        with a1:
            scheduled_day = st.date_input("Scheduled Date", value=datetime.date(2026, 8, 18))
        with a2:
            appointment_day = st.date_input("Appointment Date", value=datetime.date(2026, 8, 18))
        with a3:
            render_html("""
            <div class="indicator-box-title" style="margin-bottom: 0.1rem;">SMS Received</div>
            <div class="indicator-box-desc" style="margin-bottom: 0.2rem;">Automated reminder sent?</div>
            """)
            sms_received = st.radio("SMS Received", options=["Yes", "No"], index=1, horizontal=True, label_visibility="collapsed")
            
        render_html("</div>") # End appointment information card
        
        # PRIMARY ACTION BUTTON
        render_html("<div style='height: 8px;'></div>")
        submitted = st.form_submit_button("✦  Run AI Assessment     →", use_container_width=True)
        
    if submitted:
        # Helper for yes/no to 1/0
        def yn_to_int(val):
            return 1 if val in ["Yes", "1", 1, True] else 0
            
        try:
            if isinstance(handicap_selected, str) and (" — " in handicap_selected or " - " in handicap_selected):
                delim = " — " if " — " in handicap_selected else " - "
                handicap_val = int(handicap_selected.split(delim)[0])
            else:
                handicap_val = int(handicap_selected)
        except Exception:
            handicap_val = 0
            
        gender_code = "F" if gender in ["Female", "F"] else "M"
        
        sched_str = f"{scheduled_day}T00:00:00Z" if isinstance(scheduled_day, (datetime.date, datetime.datetime)) else str(scheduled_day)
        appt_str = f"{appointment_day}T00:00:00Z" if isinstance(appointment_day, (datetime.date, datetime.datetime)) else str(appointment_day)
        
        if isinstance(appointment_day, datetime.date) and isinstance(scheduled_day, datetime.date):
            waiting_days = max(0, (appointment_day - scheduled_day).days)
        else:
            try:
                waiting_days = max(0, (pd.to_datetime(appt_str) - pd.to_datetime(sched_str)).days)
            except Exception:
                waiting_days = 0
        
        patient_data = {
            "Gender": gender_code,
            "Age": int(age),
            "ScheduledDay": sched_str,
            "AppointmentDay": appt_str,
            "Neighbourhood": neighbourhood if neighbourhood else "ANDORINHAS",
            "Scholarship": yn_to_int(scholarship),
            "Hypertension": yn_to_int(hypertension),
            "Diabetes": yn_to_int(diabetes),
            "Alcoholism": yn_to_int(alcoholism),
            "Handicap": handicap_val,
            "SMS_received": yn_to_int(sms_received),
            "WaitingDays": waiting_days
        }
        
        print(f"[DEBUG] Processing patient payload to backend: {patient_data}")
        
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            render_html("""
            <div class="saas-card" style="text-align: center; padding: 2rem;">
                <div style="font-weight: 800; font-size: 1.15rem; color: #2563EB; margin-bottom: 0.5rem;">✦ Analyzing Patient Profile...</div>
                <div style="font-size: 0.875rem; color: #64748B;">Collecting appointment signals → Evaluating probability → Assessing vulnerability → Calculating priority</div>
            </div>
            """)
            time.sleep(0.25)
            
        try:
            models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
            result = run_pipeline(patient_data, models_dir=models_dir)
            progress_placeholder.empty()
            
            assessment_record = {
                "id": f"Assessment #{len(st.session_state.history) + 1:02d}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "probability": result["no_show_probability"],
                "risk": result["no_show_risk_category"],
                "vulnerability_cat": result["vulnerability_category"],
                "vulnerability_count": result["vulnerability_indicator_count"],
                "priority": result["follow_up_priority"],
                "patient_data": patient_data
            }
            st.session_state.history.append(assessment_record)
            st.session_state.active_assessment = assessment_record
            
        except Exception as e:
            progress_placeholder.empty()
            render_html("""
            <div class="saas-card" style="border-left: 4px solid #EF4444; background: #FEF2F2;">
                <h4 style="color: #991B1B; font-weight: 700; margin-bottom: 0.4rem;">Assessment could not be completed.</h4>
                <p style="color: #B91C1C; font-size: 0.875rem; margin: 0;">Please verify the entered information and ensure system backend artifacts are available.</p>
            </div>
            """)
            import traceback
            traceback.print_exc()
            print(f"[ERROR] Pipeline execution failed: {e}")

    # SCREEN 5: RESULTS SECTION
    if st.session_state.active_assessment:
        res = st.session_state.active_assessment
        render_html("<div style='height: 15px;'></div>")
        
        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.75rem; background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; margin-bottom: 0.4rem;">
                    <span style="width: 6px; height: 6px; background: #22C55E; border-radius: 50%;"></span> ASSESSMENT COMPLETE
                </div>
                <h3 style="color: #0F172A; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.02em; margin: 0;">
                    {res['id']}
                </h3>
                <span style="font-size: 0.8rem; color: #64748B;">Generated at {res['timestamp']}</span>
            </div>
        </div>
        """)
        
        prob_pct = res["probability"] * 100
        risk_color = {"Low": "#16A34A", "Moderate": "#D97706", "High": "#DC2626"}.get(res["risk"], "#475569")
        prio_color = {"Low": "#16A34A", "Moderate": "#D97706", "High": "#DC2626", "Highest": "#991B1B"}.get(res["priority"], "#475569")
        
        # 4 Result Metric Cards
        rc1, rc2, rc3, rc4 = st.columns(4)
        
        with rc1:
            render_html(f"""
            <div class="metric-card">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">📊</div>
                <div class="metric-title">NO-SHOW PROBABILITY</div>
                <div class="metric-value">{prob_pct:.2f}%</div>
                <div class="metric-subtitle">Model confidence score</div>
            </div>
            """)
            
        with rc2:
            render_html(f"""
            <div class="metric-card">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">⚠️</div>
                <div class="metric-title">RISK CATEGORY</div>
                <div class="metric-value" style="color: {risk_color};">{res['risk']}</div>
                <div class="metric-subtitle">Threshold: 55.0%</div>
            </div>
            """)
            
        with rc3:
            render_html(f"""
            <div class="metric-card">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">🩺</div>
                <div class="metric-title">VULNERABILITY</div>
                <div class="metric-value">{res['vulnerability_count']} Indicator{'s' if res['vulnerability_count'] != 1 else ''}</div>
                <div class="metric-subtitle">{res['vulnerability_cat']}</div>
            </div>
            """)
            
        with rc4:
            render_html(f"""
            <div class="metric-card" style="border: 2px solid {prio_color};">
                <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">🎯</div>
                <div class="metric-title">FOLLOW-UP PRIORITY</div>
                <div class="metric-value" style="color: {prio_color};">{res['priority']}</div>
                <div class="metric-subtitle">Action Tier</div>
            </div>
            """)
            
        render_html("<div style='height: 15px;'></div>")
        
        # Horizontal Probability Gauge with 40% and 55% Threshold Markers
        gauge_fill_pct = min(100.0, max(0.0, prob_pct))
        gauge_color = "#16A34A" if prob_pct < 40 else ("#D97706" if prob_pct < 55 else "#DC2626")
        
        render_html(f"""
        <div class="saas-card">
            <div class="card-header-title">
                <span>📈</span> No-Show Probability Spectrum
            </div>
            <div class="card-header-subtitle">Continuous risk distribution against calibrated operational thresholds</div>
            
            <div style="position: relative; margin-top: 1.5rem; margin-bottom: 2rem;">
                <div style="background: #E2E8F0; height: 16px; border-radius: 9999px; overflow: hidden; position: relative;">
                    <div style="background: {gauge_color}; width: {gauge_fill_pct}%; height: 100%; border-radius: 9999px; transition: width 0.6s ease-in-out;"></div>
                </div>
                
                <div style="position: absolute; left: 40%; top: -6px; bottom: -6px; width: 2px; background: #94A3B8;"></div>
                <div style="position: absolute; left: 55%; top: -6px; bottom: -6px; width: 2px; background: #DC2626; z-index: 2;"></div>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748B; font-weight: 600;">
                <span>0% (Low Risk)</span>
                <span style="color: #D97706;">40% Moderate</span>
                <span style="color: #DC2626;">55% Operating Threshold</span>
                <span>100% (High Risk)</span>
            </div>
        </div>
        """)
        
        # Follow-up Recommendation Card
        prio = res["priority"]
        if prio == "Highest":
            rec_badge = "URGENT ACTION REQUIRED"
            rec_badge_bg = "#FEF2F2"
            rec_badge_color = "#B91C1C"
            rec_title = "Highest Priority — Immediate Multichannel Outreach"
            rec_desc = "Patient exhibits high appointment cancellation/no-show risk combined with multiple documented vulnerability factors. Deploy phone call confirmation, primary caregiver notification, and offer community transportation assistance."
        elif prio == "High":
            rec_badge = "HIGH PRIORITY FOLLOW-UP"
            rec_badge_bg = "#FFFBEB"
            rec_badge_color = "#B45309"
            rec_title = "High Priority — Direct Contact & Verification"
            rec_desc = "Patient exhibits elevated risk or moderate risk with clinical vulnerability. Direct phone contact is recommended 48 hours prior to appointment to confirm attendance and address logistical barriers."
        elif prio == "Moderate":
            rec_badge = "STANDARD OPERATIONAL PROTOCOL"
            rec_badge_bg = "#EFF6FF"
            rec_badge_color = "#1D4ED8"
            rec_title = "Moderate Priority — Automated SMS & Reminder Sequence"
            rec_desc = "Patient requires standard communication protocol. Ensure automated SMS reminders are scheduled and offer easy one-click rescheduling options."
        else:
            rec_badge = "ROUTINE APPOINTMENT"
            rec_badge_bg = "#F0FDF4"
            rec_badge_color = "#15803D"
            rec_title = "Low Priority — Standard SMS Reminder"
            rec_desc = "Patient exhibits low attendance risk and zero documented vulnerability factors. Standard automated SMS reminder 24 hours prior to appointment is sufficient."
            
        render_html(f"""
        <div class="saas-card" style="border-left: 5px solid {prio_color};">
            <div style="display: inline-block; padding: 0.2rem 0.6rem; background: {rec_badge_bg}; color: {rec_badge_color}; border-radius: 6px; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 0.6rem;">
                {rec_badge}
            </div>
            <h4 style="color: #0F172A; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.4rem; letter-spacing: -0.01em;">
                {rec_title}
            </h4>
            <p style="color: #475569; font-size: 0.875rem; line-height: 1.5; margin-bottom: 1rem;">
                {rec_desc}
            </p>
            
            <div style="background: #F8FAFC; border-radius: 12px; padding: 1.15rem; border: 1px solid #E2E8F0;">
                <div style="font-size: 0.75rem; font-weight: 800; color: #475569; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.04em;">
                    Assessment Reason Breakdown:
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.825rem; color: #334155;">
                    <span>{"✓" if res['probability'] >= 0.55 else "○"} Attendance Risk: <strong>{res['risk']} ({prob_pct:.1f}%)</strong></span>
                    <span>{"✓" if res['patient_data'].get('Age', 0) >= 65 else "○"} Senior Patient (≥ 65): <strong>{res['patient_data'].get('Age', 0)} yrs</strong></span>
                    <span>{"✓" if res['patient_data'].get('Hypertension', 0) == 1 else "○"} Hypertension Documented</span>
                    <span>{"✓" if res['patient_data'].get('Diabetes', 0) == 1 else "○"} Diabetes Documented</span>
                    <span>{"✓" if res['patient_data'].get('Handicap', 0) > 0 else "○"} Handicap Documented</span>
                    <span>{"✓" if res['patient_data'].get('Alcoholism', 0) == 1 else "○"} Alcoholism Documented</span>
                </div>
            </div>
        </div>
        """)
        
        # Explainability Section
        render_html("""
        <div class="saas-card">
            <div class="card-header-title">
                <span>🔍</span> Why This Patient Was Flagged
            </div>
            <div class="card-header-subtitle">Key contributing factors derived from operational attendance and vulnerability model</div>
        """)
        
        e1, e2, e3 = st.columns(3)
        with e1:
            render_html(f"""
            <div style="padding: 1.15rem; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%;">
                <div style="font-weight: 700; color: #0F172A; font-size: 0.875rem; margin-bottom: 0.25rem;">Scheduling Lead Time</div>
                <div style="color: #64748B; font-size: 0.825rem; line-height: 1.45;">
                    Waiting period of <strong>{res['patient_data'].get('WaitingDays', 0)} days</strong> between scheduling and appointment date.
                </div>
            </div>
            """)
        with e2:
            render_html(f"""
            <div style="padding: 1.15rem; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%;">
                <div style="font-weight: 700; color: #0F172A; font-size: 0.875rem; margin-bottom: 0.25rem;">Neighbourhood Context</div>
                <div style="color: #64748B; font-size: 0.825rem; line-height: 1.45;">
                    Clinic location: <strong>{res['patient_data'].get('Neighbourhood', 'General')}</strong> based on demographic historical profile.
                </div>
            </div>
            """)
        with e3:
            sms_status = "Received" if res['patient_data'].get('SMS_received') == 1 else "Not Received"
            render_html(f"""
            <div style="padding: 1.15rem; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%;">
                <div style="font-weight: 700; color: #0F172A; font-size: 0.875rem; margin-bottom: 0.25rem;">Communication Channel</div>
                <div style="color: #64748B; font-size: 0.825rem; line-height: 1.45;">
                    SMS notification status: <strong>{sms_status}</strong> prior to appointment.
                </div>
            </div>
            """)
        render_html("</div>")


# ------------------------------------------------------------------------------
# SCREEN 6: ASSESSMENT HISTORY (SAAS AUDIT TABLE)
# ------------------------------------------------------------------------------
def render_history_screen():
    render_top_header("Assessment History")
    
    history = st.session_state.history
    
    if len(history) == 0:
        render_html("""
        <div class="saas-card" style="text-align: center; padding: 3.5rem 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📂</div>
            <h3 style="color: #0F172A; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.35rem;">No Assessment Records Yet</h3>
            <p style="color: #64748B; font-size: 0.9rem; max-width: 480px; margin: 0 auto 1.5rem auto;">
                Patient assessments executed during this session will be recorded here in an audit-ready log for clinical operations review.
            </p>
        </div>
        """)
        if st.button("✦  Run First Assessment", key="history_start_btn"):
            st.session_state.current_page = "Patient Assessment"
            st.rerun()
    else:
        render_html(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                <div>
                    <div class="card-header-title">
                        <span>📋</span> Session Assessment Log
                    </div>
                    <div class="card-header-subtitle">Audit trail of {len(history)} patient assessment(s) generated in this session</div>
                </div>
            </div>
        """)
        
        # Build Table Data
        table_rows = []
        for item in history[::-1]:
            pdata = item.get("patient_data", {})
            table_rows.append({
                "ID": item.get("id"),
                "Timestamp": item.get("timestamp"),
                "Gender": "Female" if pdata.get("Gender") == "F" else "Male",
                "Age": pdata.get("Age"),
                "Neighbourhood": pdata.get("Neighbourhood"),
                "Probability": f"{item.get('probability')*100:.2f}%",
                "Risk": item.get("risk"),
                "Vulnerability": f"{item.get('vulnerability_count')} ({item.get('vulnerability_cat')})",
                "Priority": item.get("priority")
            })
            
        df_hist = pd.DataFrame(table_rows)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        render_html("</div>")
        
        if st.button("🗑️ Clear Session History", key="clear_history_btn"):
            st.session_state.history = []
            st.session_state.active_assessment = None
            st.rerun()


# ------------------------------------------------------------------------------
# SCREEN 7: ANALYTICS (SAAS TELEMETRY DASHBOARD)
# ------------------------------------------------------------------------------
def render_analytics_screen():
    render_top_header("Analytics")
    
    history = st.session_state.history
    total = len(history)
    
    if total == 0:
        render_html("""
        <div class="saas-card" style="text-align: center; padding: 3.5rem 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📈</div>
            <h3 style="color: #0F172A; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.35rem;">No Analytics Data Available</h3>
            <p style="color: #64748B; font-size: 0.9rem; max-width: 480px; margin: 0 auto 1.5rem auto;">
                Run patient assessments to populate real-time session distribution analytics and risk cohort statistics.
            </p>
        </div>
        """)
        if st.button("✦  Launch Assessment Workflow", key="analytics_goto_assess"):
            st.session_state.current_page = "Patient Assessment"
            st.rerun()
    else:
        render_html("""
        <div style="margin-bottom: 1.25rem;">
            <h3 style="color: #0F172A; font-weight: 800; font-size: 1.35rem; margin-bottom: 0.25rem;">Session Risk Cohorts</h3>
            <p style="color: #64748B; font-size: 0.85rem; margin: 0;">Aggregate distribution across assessed patients</p>
        </div>
        """)
        
        a1, a2 = st.columns(2)
        with a1:
            with st.container(border=True):
                render_html("<h4 style='color: #0F172A; font-weight: 700; font-size: 1rem;'>Risk Category Breakdown</h4>")
                risk_counts = pd.Series([x["risk"] for x in history]).value_counts()
                st.bar_chart(risk_counts)
                
        with a2:
            with st.container(border=True):
                render_html("<h4 style='color: #0F172A; font-weight: 700; font-size: 1rem;'>Follow-up Priority Breakdown</h4>")
                prio_counts = pd.Series([x["priority"] for x in history]).value_counts()
                st.bar_chart(prio_counts)


# ------------------------------------------------------------------------------
# SCREEN 8: ABOUT MEDGUARD AI
# ------------------------------------------------------------------------------
def render_about_screen():
    render_top_header("About MedGuard AI")
    
    render_html("""
    <div class="saas-card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);">
                🩺
            </div>
            <div>
                <h3 style="color: #0F172A; font-weight: 800; font-size: 1.4rem; margin: 0;">MedGuard AI Platform</h3>
                <div style="font-size: 0.8rem; color: #64748B; font-weight: 600;">Clinical Operations Decision-Support System</div>
            </div>
        </div>
        <p style="color: #475569; font-size: 0.925rem; line-height: 1.6; margin-bottom: 1.25rem;">
            MedGuard AI is a specialized operational decision-support system designed to reduce outpatient appointment no-show rates while safeguarding vulnerable patient populations through structured, multidimensional prioritization.
        </p>
    </div>
    """)
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            render_html("""
            <h4 style="color: #0F172A; font-weight: 800; font-size: 1.05rem; margin-bottom: 0.6rem;">Production Model Specifications</h4>
            <ul style="color: #475569; font-size: 0.85rem; line-height: 1.8; padding-left: 1.2rem; margin: 0;">
                <li><strong>Architecture:</strong> Gradient Boosted Decision Trees (XGBoost)</li>
                <li><strong>Feature Dimension:</strong> Exactly 103 one-hot encoded variables</li>
                <li><strong>Calibrated Decision Threshold:</strong> 0.55 (55.0%)</li>
                <li><strong>Validation ROC-AUC:</strong> 73.69%</li>
                <li><strong>Validation PR-AUC:</strong> 43.76%</li>
            </ul>
            """)
    with c2:
        with st.container(border=True):
            render_html("""
            <h4 style="color: #0F172A; font-weight: 800; font-size: 1.05rem; margin-bottom: 0.6rem;">Priority Matrix Logic</h4>
            <ul style="color: #475569; font-size: 0.85rem; line-height: 1.8; padding-left: 1.2rem; margin: 0;">
                <li><strong>High Risk + Higher Vuln (≥ 1):</strong> Highest Priority</li>
                <li><strong>High Risk + Low Vuln (0):</strong> High Priority</li>
                <li><strong>Moderate Risk + Higher Vuln (≥ 1):</strong> High Priority</li>
                <li><strong>Moderate Risk + Low Vuln (0):</strong> Moderate Priority</li>
                <li><strong>Low Risk + Higher Vuln (≥ 1):</strong> Moderate Priority</li>
                <li><strong>Low Risk + Low Vuln (0):</strong> Low Priority</li>
            </ul>
            """)


# ------------------------------------------------------------------------------
# APPLICATION ROUTER
# ------------------------------------------------------------------------------
def main():
    if not st.session_state.authenticated:
        render_login_screen()
    else:
        render_sidebar()
        
        current_page = st.session_state.current_page
        if current_page == "Overview":
            render_overview_screen()
        elif current_page == "Patient Assessment":
            render_assessment_screen()
        elif current_page == "Assessment History":
            render_history_screen()
        elif current_page == "Analytics":
            render_analytics_screen()
        elif current_page == "About":
            render_about_screen()
        else:
            render_overview_screen()

if __name__ == "__main__":
    main()
