import streamlit as st
from streamlit_option_menu import option_menu
from config import *
from utils.api_handlers import get_wikipedia_summary
from utils.data_handlers import (
    ensure_data_directory,
    get_review_statistics,
    get_popular_destinations
)

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/yourusername/tourmind-pro',
        'Report a bug': 'https://github.com/yourusername/tourmind-pro/issues',
        'About': f"""
        # {APP_TITLE} {APP_VERSION}
        Your ultimate travel companion for discovering, planning, and
        enjoying your travels with intelligent recommendations and
        real-time information.
        Built with ❤️ using Streamlit
        """
    }
)

# ============================================
# CUSTOM CSS — TRAVEL / NATURE INSPIRED THEME
# ============================================

st.markdown("""
<style>

/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Nunito:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {
    --forest:    #2D5016;
    --leaf:      #4A7C59;
    --sage:      #7AAE8E;
    --mist:      #C8DDD4;
    --sand:      #E8D5A3;
    --dune:      #C9A96E;
    --earth:     #8B6E47;
    --bark:      #4A3728;
    --sky:       #87CEEB;
    --ocean:     #2E86AB;
    --sunset:    #E8845A;
    --golden:    #F4B942;
    --cream:     #FAF7F0;
    --white:     #FFFFFF;
    --text-dark: #2C2416;
    --text-mid:  #5C4A32;
    --text-soft: #8B7355;
    --card-bg:   rgba(250,247,240,0.92);
    --glass:     rgba(255,255,255,0.15);
    --shadow-sm: 0 2px 12px rgba(44,36,22,0.08);
    --shadow-md: 0 6px 30px rgba(44,36,22,0.14);
    --shadow-lg: 0 16px 60px rgba(44,36,22,0.22);
    --radius-sm: 10px;
    --radius-md: 18px;
    --radius-lg: 28px;
    --radius-xl: 40px;
    --ff-display: 'Playfair Display', Georgia, serif;
    --ff-body:    'Nunito', sans-serif;
}

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: var(--ff-body);
    color: var(--text-dark);
}

/* ── Background ── */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 10% 0%,   rgba(74,124,89,0.18) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 20%,  rgba(135,206,235,0.15) 0%, transparent 45%),
        radial-gradient(ellipse at 50% 100%, rgba(232,213,163,0.25) 0%, transparent 55%),
        linear-gradient(160deg, #f0ede4 0%, #eee8d8 40%, #e8f0ea 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

/* Subtle leaf-vein texture overlay */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg width='120' height='120' viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M60 10 Q90 40 60 110 Q30 40 60 10Z' fill='none' stroke='%234A7C59' stroke-width='0.4' opacity='0.06'/%3E%3C/svg%3E");
    background-size: 140px 140px;
    pointer-events: none;
    z-index: 0;
}

/* ── Hide defaults ── */
[data-testid="stSidebar"]  { display: none; }
#MainMenu                  { visibility: hidden; }
footer                     { visibility: hidden; }
.main                      { padding: 0 1rem; position: relative; z-index: 1; }

/* ── Navigation Bar ── */
[data-testid="stHorizontalBlock"] > div:first-child { z-index: 100; }

/* ── Divider ── */
hr {
    border: none;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, var(--sage), var(--dune), transparent);
    margin: 2rem 0;
    opacity: 0.5;
}

/* ── Headings ── */
h1 {
    font-family: var(--ff-display);
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700;
    color: var(--forest);
    letter-spacing: -0.5px;
    padding-bottom: 0.4rem;
    border-bottom: 3px solid var(--leaf);
    margin-bottom: 0.6rem;
}

h2 {
    font-family: var(--ff-display);
    font-size: clamp(1.4rem, 2.5vw, 2rem);
    font-weight: 700;
    color: var(--bark);
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
}

h3 {
    font-family: var(--ff-body);
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--earth);
}

/* ── Buttons ── */
.stButton > button {
    font-family: var(--ff-body) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.4px;
    width: 100%;
    border-radius: var(--radius-md) !important;
    height: 3em;
    background: linear-gradient(135deg, var(--leaf) 0%, var(--forest) 100%) !important;
    color: var(--white) !important;
    border: none !important;
    box-shadow: 0 4px 18px rgba(45,80,22,0.3) !important;
    transition: all 0.28s cubic-bezier(0.34,1.56,0.64,1) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: "";
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
    transition: left 0.5s ease;
}

.stButton > button:hover::before { left: 100%; }

.stButton > button:hover {
    background: linear-gradient(135deg, var(--sage) 0%, var(--leaf) 100%) !important;
    box-shadow: 0 8px 28px rgba(45,80,22,0.4) !important;
    transform: translateY(-3px) scale(1.01) !important;
}

.stButton > button:active {
    transform: translateY(0px) scale(0.99) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--card-bg);
    border: 1px solid rgba(74,124,89,0.2);
    border-radius: var(--radius-md);
    padding: 1.2rem 1.5rem !important;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(8px);
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}

[data-testid="stMetricLabel"] {
    font-family: var(--ff-body);
    color: var(--text-soft) !important;
    font-size: 0.85rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

[data-testid="stMetricValue"] {
    font-family: var(--ff-display) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--forest) !important;
}

[data-testid="stMetricDelta"] {
    font-family: var(--ff-body);
    font-size: 0.8rem !important;
    color: var(--leaf) !important;
}

/* ── Alert / Info Boxes ── */
.stAlert {
    border-radius: var(--radius-md) !important;
    border: none !important;
    font-family: var(--ff-body) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid rgba(74,124,89,0.18) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-sm) !important;
    backdrop-filter: blur(6px);
}

/* ── Selectbox / Input ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea textarea {
    font-family: var(--ff-body) !important;
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid rgba(74,124,89,0.25) !important;
    background: rgba(250,247,240,0.9) !important;
    color: var(--text-dark) !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--leaf) !important;
    box-shadow: 0 0 0 3px rgba(74,124,89,0.15) !important;
}

/* ── Selectbox dropdown — GLOBAL fix for all pages ── */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] ul,
[role="listbox"],
[data-baseweb="menu"],
[data-baseweb="menu"] > ul {
    background: #ffffff !important;
    border: 1.5px solid rgba(74,124,89,0.22) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 28px rgba(44,36,22,0.14) !important;
    overflow: hidden !important;
}

/* Dropdown option items */
[role="option"],
[data-baseweb="menu"] li,
[data-baseweb="popover"] li {
    background: #ffffff !important;
    color: #1a1a1a !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 8px 14px !important;
}

/* Option hover state */
[role="option"]:hover,
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover {
    background: rgba(74,124,89,0.10) !important;
    color: #2D5016 !important;
    cursor: pointer !important;
}

/* Selected option */
[aria-selected="true"][role="option"],
[data-baseweb="menu"] li[aria-selected="true"] {
    background: rgba(74,124,89,0.15) !important;
    color: #2D5016 !important;
    font-weight: 700 !important;
}

/* Dropdown option text */
[role="option"] span,
[data-baseweb="menu"] li span {
    color: #1a1a1a !important;
    font-family: 'Nunito', sans-serif !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(200,221,212,0.4) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    gap: 2px !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: var(--ff-body) !important;
    font-weight: 600 !important;
    color: var(--text-mid) !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 20px !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--leaf), var(--forest)) !important;
    color: white !important;
    box-shadow: 0 3px 12px rgba(45,80,22,0.3) !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--leaf) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 7px; }
::-webkit-scrollbar-track { background: var(--mist); }
::-webkit-scrollbar-thumb {
    background: var(--sage);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: var(--leaf); }

/* ── Hero Section ── */
.tm-hero {
    position: relative;
    border-radius: var(--radius-xl);
    overflow: hidden;
    padding: clamp(1.4rem, 5vw, 5rem) clamp(1rem, 4vw, 3.5rem);
    margin-bottom: 2rem;
    background:
        linear-gradient(135deg,
            rgba(45,80,22,0.88) 0%,
            rgba(74,124,89,0.75) 40%,
            rgba(46,134,171,0.65) 100%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cdefs%3E%3CradialGradient id='a' cx='50%25' cy='50%25'%3E%3Cstop offset='0' stop-color='%234A7C59' stop-opacity='.6'/%3E%3Cstop offset='1' stop-color='%232D5016' stop-opacity='0'/%3E%3C/radialGradient%3E%3C/defs%3E%3Cellipse cx='200' cy='200' rx='200' ry='200' fill='url(%23a)'/%3E%3C/svg%3E") center/cover;
    box-shadow: var(--shadow-lg);
    animation: heroReveal 0.9s cubic-bezier(0.22,1,0.36,1) both;
}

@keyframes heroReveal {
    from { opacity:0; transform: translateY(24px) scale(0.98); }
    to   { opacity:1; transform: translateY(0)   scale(1); }
}

.tm-hero::after {
    content: "";
    position: absolute;
    bottom: -2px; left: 0; right: 0;
    height: 80px;
    background: linear-gradient(to bottom, transparent, rgba(240,237,228,0.6));
}

.tm-hero-tag {
    display: inline-block;
    background: rgba(244,185,66,0.25);
    border: 1px solid rgba(244,185,66,0.5);
    color: var(--golden);
    font-family: var(--ff-body);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding: 5px 16px;
    border-radius: 99px;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(6px);
    animation: fadeUp 0.7s 0.2s both;
}

.tm-hero-title {
    font-family: var(--ff-display);
    font-size: clamp(2.2rem, 5vw, 4rem);
    font-weight: 700;
    color: var(--white);
    line-height: 1.15;
    margin: 0 0 1rem;
    text-shadow: 0 2px 20px rgba(0,0,0,0.25);
    animation: fadeUp 0.7s 0.35s both;
}

.tm-hero-title em {
    font-style: italic;
    color: var(--sand);
}

.tm-hero-sub {
    font-family: var(--ff-body);
    font-size: 1.1rem;
    color: rgba(255,255,255,0.88);
    line-height: 1.65;
    max-width: min(580px, 100%);
    margin: 0;
    animation: fadeUp 0.7s 0.5s both;
}

/* ── Feature Cards ── */
.tm-feature-card {
    background: var(--card-bg);
    border: 1px solid rgba(74,124,89,0.15);
    border-radius: var(--radius-lg);
    padding: 1.8rem;
    height: 100%;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(10px);
    transition: transform 0.28s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.28s ease,
                border-color 0.28s ease;
    animation: fadeUp 0.6s both;
    position: relative;
    overflow: hidden;
}

.tm-feature-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    background: linear-gradient(90deg, var(--leaf), var(--ocean));
    opacity: 0;
    transition: opacity 0.25s;
}

.tm-feature-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-md); border-color: rgba(74,124,89,0.3); }
.tm-feature-card:hover::before { opacity: 1; }

.tm-feature-icon {
    font-size: 2.4rem;
    margin-bottom: 0.8rem;
    display: block;
    filter: drop-shadow(0 2px 6px rgba(74,124,89,0.3));
}

.tm-feature-title {
    font-family: var(--ff-display);
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--forest);
    margin: 0 0 0.6rem;
}

.tm-feature-desc {
    font-family: var(--ff-body);
    font-size: 0.9rem;
    color: var(--text-soft);
    line-height: 1.65;
    margin: 0;
}

/* ── Destination Pill Cards ── */
.tm-dest-card {
    background: linear-gradient(135deg, var(--card-bg), rgba(200,221,212,0.5));
    border: 1.5px solid rgba(74,124,89,0.22);
    border-radius: var(--radius-md);
    padding: 1.4rem 1rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(8px);
    transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s ease;
    animation: fadeUp 0.5s both;
}

.tm-dest-card:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: var(--shadow-md);
}

.tm-dest-name {
    font-family: var(--ff-display);
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--forest);
    margin: 0 0 0.35rem;
}

.tm-dest-count {
    font-family: var(--ff-body);
    font-size: 0.82rem;
    color: var(--text-soft);
    margin: 0;
    font-weight: 500;
}

.tm-dest-badge {
    display: inline-block;
    width: 28px; height: 28px;
    background: linear-gradient(135deg, var(--golden), var(--sunset));
    border-radius: 50%;
    line-height: 28px;
    font-size: 0.75rem;
    color: white;
    font-weight: 700;
    margin-bottom: 0.6rem;
}

/* ── How-to Steps ── */
.tm-step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 1.2rem;
    border-radius: var(--radius-md);
    background: rgba(200,221,212,0.25);
    margin-bottom: 0.75rem;
    border: 1px solid rgba(74,124,89,0.12);
    transition: background 0.2s, transform 0.2s;
}

.tm-step:hover {
    background: rgba(200,221,212,0.5);
    transform: translateX(6px);
}

.tm-step-num {
    flex-shrink: 0;
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--leaf), var(--forest));
    color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--ff-display);
    font-size: 0.95rem;
    font-weight: 700;
    box-shadow: 0 3px 10px rgba(45,80,22,0.3);
}

.tm-step-text {
    font-family: var(--ff-body);
    font-size: 0.92rem;
    color: var(--text-mid);
    line-height: 1.5;
    margin: 0;
    padding-top: 6px;
}

.tm-step-text strong { color: var(--forest); }

/* ── Tip Box ── */
.tm-tip-box {
    background: linear-gradient(135deg,
        rgba(244,185,66,0.12), rgba(232,132,90,0.10));
    border: 1.5px solid rgba(244,185,66,0.35);
    border-radius: var(--radius-md);
    padding: 1.4rem 1.5rem;
    backdrop-filter: blur(6px);
    box-shadow: var(--shadow-sm);
}

.tm-tip-box h4 {
    font-family: var(--ff-display);
    color: var(--earth);
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 0.6rem;
}

.tm-tip-box p {
    font-family: var(--ff-body);
    font-size: 0.88rem;
    color: var(--text-mid);
    margin: 0;
    line-height: 1.6;
}

/* ── Section Header ── */
.tm-section-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}

.tm-section-header .tm-sh-icon {
    width: 46px; height: 46px;
    background: linear-gradient(135deg, var(--leaf), var(--forest));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 4px 14px rgba(45,80,22,0.28);
    flex-shrink: 0;
}

.tm-section-header .tm-sh-text h2 {
    margin: 0 !important;
    padding: 0;
    font-size: 1.4rem !important;
}

.tm-section-header .tm-sh-text p {
    font-size: 0.82rem;
    color: var(--text-soft);
    margin: 2px 0 0;
    font-family: var(--ff-body);
}

/* ── Footer ── */
.tm-footer {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-top: 1.5px solid rgba(74,124,89,0.18);
    margin-top: 1rem;
}

.tm-footer p {
    font-family: var(--ff-body);
    color: var(--text-soft);
    font-size: 0.85rem;
    margin: 0;
    letter-spacing: 0.3px;
}

.tm-footer span {
    color: var(--leaf);
    font-weight: 700;
}

/* ── API Config Banner ── */
.tm-api-banner {
    background: linear-gradient(135deg,
        rgba(232,132,90,0.12), rgba(244,185,66,0.10));
    border: 1.5px solid rgba(232,132,90,0.3);
    border-radius: var(--radius-md);
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Stagger cards */
.tm-feature-card:nth-child(1) { animation-delay: 0.05s; }
.tm-feature-card:nth-child(2) { animation-delay: 0.12s; }
.tm-feature-card:nth-child(3) { animation-delay: 0.19s; }
.tm-dest-card:nth-child(1) { animation-delay: 0.0s; }
.tm-dest-card:nth-child(2) { animation-delay: 0.07s; }
.tm-dest-card:nth-child(3) { animation-delay: 0.14s; }
.tm-dest-card:nth-child(4) { animation-delay: 0.21s; }
.tm-dest-card:nth-child(5) { animation-delay: 0.28s; }

/* ============================================================
   RESPONSIVE / MOBILE-FIRST OVERRIDES
   Breakpoints: 768px (tablet), 480px (mobile)
   ============================================================ */

/* ── Streamlit core layout ── */
@media (max-width: 768px) {
    .main { padding: 0 0.5rem !important; }

    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"],
    .block-container {
        padding-left:  0.5rem !important;
        padding-right: 0.5rem !important;
        max-width:     100% !important;
    }
}

/* ── Navigation bar — shrink on mobile ── */
@media (max-width: 768px) {
    .nav-link {
        font-size: 11px !important;
        padding:   8px 6px !important;
    }
    .nav-link .icon { font-size: 13px !important; }
}

/* ── Hero section ── */
@media (max-width: 768px) {
    .tm-hero {
        padding:       2rem 1.2rem !important;
        border-radius: 16px !important;
        margin-bottom: 1.2rem !important;
    }
    .tm-hero::after { font-size: 3rem !important; right: 1rem !important; }
    .tm-hero-title  { font-size: clamp(1.4rem, 6vw, 2rem) !important; }
    .tm-hero-sub    { font-size: 0.88rem !important; }
    .tm-hero-tag    { font-size: 0.65rem !important; padding: 3px 10px !important; }
}

/* ── Hero banners on all pages ── */
@media (max-width: 768px) {
    .tm-chat-hero, .tm-dest-hero, .tm-itin-hero,
    .tm-places-hero, .tm-rev-hero, .tm-peak-hero {
        padding:       1.6rem 1.2rem !important;
        border-radius: 16px !important;
        margin-bottom: 1.2rem !important;
    }
    .tm-chat-hero::after, .tm-dest-hero::after,
    .tm-itin-hero::after, .tm-places-hero::after,
    .tm-rev-hero::after,  .tm-peak-hero::after {
        display: none !important;
    }
    .tm-chat-hero h1, .tm-dest-hero h1, .tm-itin-hero h1,
    .tm-places-hero h1, .tm-rev-hero h1, .tm-peak-hero h1 {
        font-size: 1.4rem !important;
    }
}

/* ── Feature cards — stack on mobile ── */
@media (max-width: 768px) {
    .tm-feature-card {
        padding:       1.2rem !important;
        border-radius: 14px !important;
        margin-bottom: 0.8rem !important;
    }
    .tm-feature-icon { font-size: 1.8rem !important; }
    .tm-feature-title { font-size: 1rem !important; }
    .tm-feature-desc  { font-size: 0.82rem !important; }
}

/* ── Destination trending cards ── */
@media (max-width: 768px) {
    .tm-dest-card   { padding: 0.9rem 0.6rem !important; }
    .tm-dest-name   { font-size: 0.88rem !important; }
    .tm-dest-count  { font-size: 0.72rem !important; }
    .tm-dest-badge  { width: 22px; height: 22px; font-size: 0.65rem; }
}

/* ── Steps (getting started) ── */
@media (max-width: 768px) {
    .tm-step { padding: 0.7rem 0.9rem !important; }
    .tm-step-num { width: 30px; height: 30px; font-size: 0.82rem; }
    .tm-step-text { font-size: 0.82rem !important; }
}

/* ── Metrics ── */
@media (max-width: 768px) {
    [data-testid="stMetric"] {
        padding: 0.8rem 1rem !important;
    }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
}

/* ── Section headers ── */
@media (max-width: 768px) {
    .tm-section-header .tm-sh-icon,
    .tm-sec-head .icon-box {
        width: 36px !important; height: 36px !important;
        font-size: 1rem !important;
    }
    .tm-section-header .tm-sh-text h2,
    .tm-sec-head .sec-title { font-size: 1.1rem !important; }
    .tm-sec-head .sec-sub   { font-size: 0.72rem !important; }
}

/* ── Place cards ── */
@media (max-width: 768px) {
    .tm-place-card  { border-radius: 16px !important; margin-bottom: 1rem !important; }
    .tm-place-name  { font-size: 1.1rem !important; }
    .tm-meta-pill   { font-size: 0.72rem !important; padding: 3px 8px !important; }
    .tm-wiki-snippet { font-size: 0.82rem !important; }
}

/* ── Review cards ── */
@media (max-width: 768px) {
    .tm-review-card    { padding: 1rem 1.1rem !important; border-radius: 14px !important; }
    .tm-review-place   { font-size: 0.95rem !important; }
    .tm-review-comment { font-size: 0.82rem !important; }
    .tm-rev-count      { font-size: 0.78rem !important; }
}

/* ── Stats row (reviews page) ── */
@media (max-width: 768px) {
    .tm-stats-row {
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 0.5rem !important;
    }
    .tm-stat-card { padding: 0.7rem 0.5rem !important; border-radius: 12px !important; }
    .tm-stat-val  { font-size: 1.3rem !important; }
    .tm-stat-lbl  { font-size: 0.62rem !important; letter-spacing: 0.8px !important; }
}

/* ── Peak hours info grid ── */
@media (max-width: 768px) {
    .tm-info-grid {
        grid-template-columns: 1fr !important;
        gap: 0.6rem !important;
    }
    .tm-info-tile .tile-value { font-size: 0.88rem !important; }
    .tm-info-tile .tile-label { font-size: 0.65rem !important; }
}

/* ── Crowd bars ── */
@media (max-width: 768px) {
    .tm-crowd-wrap  { padding: 1rem 1.1rem !important; border-radius: 14px !important; }
    .tm-crowd-bar-outer { height: 11px !important; }
    .tm-crowd-badge { font-size: 0.85rem !important; }
}

/* ── Nearby attraction cards ── */
@media (max-width: 768px) {
    .tm-nearby-card { flex-direction: column !important; border-radius: 14px !important; }
    .tm-nearby-img  { width: 100% !important; max-height: 160px !important; object-fit: cover; }
    .tm-nearby-body { padding: 0.8rem 1rem !important; }
    .tm-nearby-name { font-size: 0.95rem !important; }
}

/* ── Recommendation cards (peak hours) ── */
@media (max-width: 768px) {
    .tm-rec-card { padding: 1rem 1.1rem !important; border-radius: 14px !important; }
    .tm-rec-card .rec-icon { font-size: 1.3rem !important; }
    .tm-rec-card .rec-text { font-size: 0.82rem !important; }
}

/* ── Itinerary result card ── */
@media (max-width: 768px) {
    .tm-result-card { padding: 1.2rem 1.3rem !important; border-radius: 16px !important; }
    .tm-result-card p, .tm-result-card li { font-size: 0.85rem !important; }
}

/* ── Tip strips / boxes ── */
@media (max-width: 768px) {
    .tm-tip-strip, .tm-tip-box {
        padding: 0.8rem 1rem !important;
        border-radius: 12px !important;
    }
    .tm-tip-strip p, .tm-tip-box p { font-size: 0.80rem !important; }
}

/* ── Sort / count pills ── */
@media (max-width: 768px) {
    .tm-count-pills { gap: 5px !important; }
    .tm-sort-pills  { gap: 5px !important; }
    .tm-count-pill, .stButton > button {
        font-size: 0.78rem !important;
        padding:   4px 8px !important;
    }
}

/* ── Tabs ── */
@media (max-width: 768px) {
    [data-baseweb="tab"] {
        font-size: 0.8rem !important;
        padding:   6px 12px !important;
    }
}

/* ── Forms ── */
@media (max-width: 768px) {
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        font-size: 0.88rem !important;
    }
    [data-testid="stFormSubmitButton"] button {
        font-size: 0.88rem !important;
        height: 2.8em !important;
    }
}

/* ── Chat input (mobile) ── */
@media (max-width: 768px) {
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div,
    [data-testid="stBottom"] > div > div > div {
        padding: 6px 8px !important;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 0.85rem !important;
    }
}

/* ── Chat bubbles ── */
@media (max-width: 768px) {
    [data-testid="stChatMessage"] {
        border-radius: 12px !important;
        padding: 0.6rem !important;
    }
}

/* ── Empty states ── */
@media (max-width: 768px) {
    .tm-empty-state { padding: 1.8rem 0.8rem !important; }
    .tm-empty-state .es-icon { font-size: 2.2rem !important; }
    .tm-empty-state p { font-size: 0.82rem !important; }
}

/* ── Suggestion chips (chatbot) ── */
@media (max-width: 768px) {
    .tm-chips-wrap { gap: 6px !important; margin: 0.6rem 0 1rem !important; }
    .tm-chip { font-size: 0.75rem !important; padding: 5px 10px !important; }
}

/* ── Dividers ── */
@media (max-width: 768px) {
    .tm-divider { margin: 1rem 0 !important; }
    hr { margin: 1.2rem 0 !important; }
}

/* ── Footer ── */
@media (max-width: 768px) {
    .tm-footer { padding: 1.2rem 0.5rem 0.5rem !important; }
    .tm-footer p { font-size: 0.75rem !important; }
}

/* ── Scrollbar hidden on mobile ── */
@media (max-width: 480px) {
    ::-webkit-scrollbar { width: 0 !important; }
}

/* ── Very small screens (≤480px) ── */
@media (max-width: 480px) {
    .tm-hero { padding: 1.4rem 1rem !important; }
    .tm-hero-title { font-size: 1.2rem !important; }
    .tm-hero-sub   { font-size: 0.80rem !important; }

    .tm-stats-row {
        grid-template-columns: 1fr 1fr !important;
    }
    .tm-stat-val { font-size: 1.1rem !important; }

    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }

    .tm-place-name { font-size: 0.95rem !important; }
    .tm-review-place { font-size: 0.88rem !important; }

    .nav-link { font-size: 9px !important; padding: 6px 3px !important; }
    .nav-link .icon { font-size: 11px !important; }
}


</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE
# ============================================

ensure_data_directory()

# ============================================
# HORIZONTAL NAVIGATION BAR
# ============================================

selected = option_menu(
    menu_title=None,
    options=["Home", "Places", "Reviews", "Itinerary", "Chatbot", "Weather", "Peak Hours"],
    icons=["house-fill", "map-fill", "star-fill", "calendar2-check-fill",
           "chat-dots-fill", "cloud-sun-fill", "clock-fill"],
    menu_icon="compass",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0 !important",
            "background": "linear-gradient(135deg, #2D5016 0%, #3A6B2A 50%, #1E3A6B 100%)",
            "box-shadow": "0 4px 24px rgba(45,80,22,0.3)",
        },
        "icon": {
            "color": "rgba(255,255,255,0.75)",
            "font-size": "16px",
        },
        "nav-link": {
            "font-family": "'Nunito', sans-serif",
            "font-size": "14px",
            "font-weight": "600",
            "text-align": "center",
            "margin": "0px",
            "padding": "14px 18px",
            "color": "rgba(255,255,255,0.85)",
            "--hover-color": "rgba(232,213,163,0.18)",
            "letter-spacing": "0.3px",
            "transition": "all 0.2s ease",
        },
        "nav-link-selected": {
            "background": "rgba(244,185,66,0.28)",
            "color": "#F4B942",
            "border-bottom": "3px solid #F4B942",
        },
    }
)

st.markdown("---")

# ============================================
# PAGE ROUTING
# ============================================

if selected == "Home":

    # ── HERO ─────────────────────────────────
    st.markdown("""
    <div class="tm-hero">
        <div class="tm-hero-tag">🌿 Your Travel Companion</div>
        <h1 class="tm-hero-title">
            Discover the World,<br><em>One Journey at a Time</em>
        </h1>
        <p class="tm-hero-sub">
            Welcome to <strong style="color:#F4B942;">TourMind</strong> — your all-in-one intelligent travel guide.
            Explore breathtaking destinations, craft personalised itineraries,
            check live weather, and connect with a community of passionate travellers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── API STATUS ────────────────────────────
    api_status   = check_api_keys()
    missing_keys = get_missing_keys()

    if missing_keys:
        with st.expander("⚠️  API Configuration — Click to Setup", expanded=False):
            st.markdown("""
            <div class="tm-api-banner">
                <strong>Some API keys are not configured.</strong>
                The app will run with limited functionality until they are added.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Missing Keys:**")
                for key in missing_keys:
                    st.markdown(f"- ❌ `{key}`")
            with col2:
                st.markdown("**Configured Keys:**")
                if api_status["unsplash"]:
                    st.markdown("- ✅ Unsplash API")
                if api_status["openweather"]:
                    st.markdown("- ✅ OpenWeatherMap API")
                st.markdown("- ✅ Wikipedia API (no key needed)")

            st.info("""
            **Quick Setup:**
            1. Open `.streamlit/secrets.toml`
            2. Add your API keys
            3. Save & restart the app

            Get free keys → [Unsplash](https://unsplash.com/developers) · [OpenWeatherMap](https://openweathermap.org/appid)
            """)

    # ── FEATURES ─────────────────────────────
    st.markdown("""
    <div class="tm-section-header">
        <div class="tm-sh-icon">🎯</div>
        <div class="tm-sh-text">
            <h2>Explore Features</h2>
            <p>Everything you need for the perfect trip</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("🏖️", "Place Recommendations",
         "Discover top tourist destinations with stunning photos, detailed Wikipedia info, and Google Maps integration."),
        ("⭐", "Reviews & Ratings",
         "Read authentic experiences from fellow travellers and share your own reviews to help the community."),
        ("🗓️", "Itinerary Planner",
         "Create personalised day-by-day travel plans tailored to your preferences and trip duration."),
        ("💬", "Chatbot Assistant",
         "Get instant answers to travel questions with our AI-powered assistant available around the clock."),
        ("🌤️", "Destination Info & Weather",
         "Check real-time weather forecasts, view destination images, and read comprehensive Wikipedia articles."),
        ("⏰", "Peak Hours & Nearby",
         "Find the best visiting times, avoid crowds, and uncover hidden gems near your destination."),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="tm-feature-card">
                <span class="tm-feature-icon">{icon}</span>
                <p class="tm-feature-title">{title}</p>
                <p class="tm-feature-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── STATISTICS ───────────────────────────
    st.markdown("""
    <div class="tm-section-header">
        <div class="tm-sh-icon">📊</div>
        <div class="tm-sh-text">
            <h2>App Statistics</h2>
            <p>Live insights from our community</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    stats = get_review_statistics()
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Reviews",  stats["total_reviews"],
                  "Growing daily" if stats["total_reviews"] > 0 else None)
    with c2:
        st.metric("Average Rating",
                  f"{stats['average_rating']} ⭐" if stats["total_reviews"] > 0 else "N/A")
    with c3:
        st.metric("Places Reviewed", stats["total_places"])
    with c4:
        st.metric("API Status",
                  "🟢 Active" if (api_status.get("unsplash") and api_status.get("openweather")) else "🟡 Limited")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── TRENDING ─────────────────────────────
    st.markdown("""
    <div class="tm-section-header">
        <div class="tm-sh-icon">🔥</div>
        <div class="tm-sh-text">
            <h2>Trending Destinations</h2>
            <p>Most-reviewed places by our travellers</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    popular = get_popular_destinations(limit=5)

    if popular:
        dest_cols = st.columns(min(5, len(popular)))
        for idx, (place, count) in enumerate(popular):
            with dest_cols[idx]:
                st.markdown(f"""
                <div class="tm-dest-card">
                    <div class="tm-dest-badge">#{idx+1}</div>
                    <p class="tm-dest-name">{place}</p>
                    <p class="tm-dest-count">🗺️ {count} review{"s" if count != 1 else ""}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🌍 No reviews yet — be the first to share your travel experience!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── GETTING STARTED ───────────────────────
    st.markdown("""
    <div class="tm-section-header">
        <div class="tm-sh-icon">🚀</div>
        <div class="tm-sh-text">
            <h2>Getting Started</h2>
            <p>Your guide to using TourMind</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_steps, col_tips = st.columns([3, 2], gap="large")

    with col_steps:
        steps = [
            ("🏖️", "Discover Places",       "Click <strong>Places</strong> in the navbar to search destinations"),
            ("⭐", "Read Reviews",           "Visit <strong>Reviews</strong> to see real traveller experiences"),
            ("🗓️", "Plan Your Trip",         "Use <strong>Itinerary</strong> to build detailed travel schedules"),
            ("🌤️", "Check Weather",          "Go to <strong>Weather</strong> for live forecasts & destination info"),
            ("⏰", "Optimise Your Timing",   "Click <strong>Peak Hours</strong> to find the best visiting windows"),
            ("💬", "Ask the Chatbot",        "Use <strong>Chatbot</strong> for instant AI-powered travel advice"),
        ]
        for i, (icon, title, detail) in enumerate(steps, 1):
            st.markdown(f"""
            <div class="tm-step">
                <div class="tm-step-num">{i}</div>
                <p class="tm-step-text"><strong>{icon} {title}</strong><br>{detail}</p>
            </div>
            """, unsafe_allow_html=True)

    with col_tips:
        st.markdown("""
        <div class="tm-tip-box">
            <h4>💡 Pro Tips</h4>
            <p>
                📍 Use specific city or state names for better search results.<br><br>
                ⭐ Leave reviews to help fellow travellers discover great spots.<br><br>
                🗺️ Use the Google Maps integration for seamless navigation.<br><br>
                🌐 Ensure API keys are configured for the full experience.<br><br>
                🔁 Refresh the page if real-time data doesn't load on first try.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── FOOTER ───────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div class="tm-footer">
        <p>Made with <span>♥</span> for travellers around the world &nbsp;·&nbsp; © 2026 <span>TourMind AI</span></p>
    </div>
    """, unsafe_allow_html=True)


elif selected == "Places":
    from pages import place_recommendations
    place_recommendations.show()

elif selected == "Reviews":
    from pages import reviews_and_ratings
    reviews_and_ratings.show()

elif selected == "Itinerary":
    from pages import itinerary_planner
    itinerary_planner.show()

elif selected == "Chatbot":
    from pages import chatbot_assistant
    chatbot_assistant.show()

elif selected == "Weather":
    from pages import destination_info
    destination_info.show()

elif selected == "Peak Hours":
    from pages import peak_hours_nearby
    peak_hours_nearby.show()
