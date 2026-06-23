"""
Destination Info Page — Travel/Nature Theme
"""
import streamlit as st
from utils.api_handlers import get_weather_forecast, get_unsplash_image, get_wikipedia_summary


def show():

    # ============================================
    # PAGE STYLES
    # ============================================

    st.markdown("""
    <style>
    /* ── Hero ── */
    .tm-dest-hero {
        background: linear-gradient(135deg,
            rgba(46,134,171,0.88) 0%,
            rgba(45,80,22,0.80) 55%,
            rgba(74,124,89,0.75) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(46,134,171,0.22);
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }
    .tm-dest-hero::after {
        content: "🌤️";
        position: absolute;
        right: 2.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 5.5rem;
        opacity: 0.10;
        pointer-events: none;
    }
    .tm-dest-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .tm-dest-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        margin: 0;
        line-height: 1.6;
    }
    .tm-dest-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(135,206,235,0.22);
        border: 1px solid rgba(135,206,235,0.45);
        color: #87CEEB;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        padding: 4px 14px;
        border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── Search Card ── */
    .tm-search-card {
        background: rgba(250,247,240,0.92);
        border: 1.5px solid rgba(74,124,89,0.18);
        border-radius: 20px;
        padding: 1.8rem 2rem;
        box-shadow: 0 4px 24px rgba(44,36,22,0.09);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        animation: fadeUp 0.5s 0.1s both;
    }

    /* ── Section header ── */
    .tm-sec-head {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1.2rem;
    }
    .tm-sec-head .icon-box {
        width: 42px; height: 42px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 14px rgba(45,80,22,0.22);
        flex-shrink: 0;
    }
    .tm-sec-head .icon-box.green  { background: linear-gradient(135deg,#4A7C59,#2D5016); }
    .tm-sec-head .icon-box.blue   { background: linear-gradient(135deg,#2E86AB,#1A5F7A); }
    .tm-sec-head .icon-box.golden { background: linear-gradient(135deg,#C9A96E,#8B6E47); }
    .tm-sec-head .sec-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #2D5016;
        margin: 0;
    }
    .tm-sec-head .sec-sub {
        font-family: 'Nunito', sans-serif;
        font-size: 0.8rem;
        color: #8B7355;
        margin: 2px 0 0;
    }

    /* ── Column vertical alignment ── */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-end;
    }

    /* ── Gallery cards ── */
    .tm-photo-wrap {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 24px rgba(44,36,22,0.16);
        transition: transform 0.28s cubic-bezier(0.34,1.56,0.64,1),
                    box-shadow 0.28s ease;
        animation: fadeUp 0.5s both;
    }
    .tm-photo-wrap:nth-child(1) { animation-delay: 0.05s; }
    .tm-photo-wrap:nth-child(2) { animation-delay: 0.12s; }
    .tm-photo-wrap:nth-child(3) { animation-delay: 0.19s; }
    .tm-photo-wrap:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 14px 40px rgba(44,36,22,0.22);
    }
    .tm-photo-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to top, rgba(45,80,22,0.55) 0%, transparent 55%);
        opacity: 0;
        transition: opacity 0.25s;
    }
    .tm-photo-wrap:hover .tm-photo-overlay { opacity: 1; }

    /* ── Current weather card ── */
    .tm-weather-now {
        background: linear-gradient(135deg,
            rgba(46,134,171,0.14), rgba(45,80,22,0.08));
        border: 1.5px solid rgba(46,134,171,0.22);
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 18px rgba(46,134,171,0.10);
        animation: fadeUp 0.5s both;
    }
    .tm-weather-label {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #7AAE8E;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 0 1rem;
    }

    /* ── Forecast day cards ── */
    .tm-forecast-card {
        background: rgba(250,247,240,0.92);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 16px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        box-shadow: 0 3px 14px rgba(44,36,22,0.08);
        backdrop-filter: blur(6px);
        transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s;
        animation: fadeUp 0.5s both;
    }
    .tm-forecast-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 28px rgba(44,36,22,0.14);
    }
    .tm-fc-date {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #7AAE8E;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 0.5rem;
    }
    .tm-fc-high {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #E8845A;
        margin: 0;
    }
    .tm-fc-low {
        font-family: 'Nunito', sans-serif;
        font-size: 0.9rem;
        color: #2E86AB;
        font-weight: 600;
        margin: 2px 0 0.4rem;
    }
    .tm-fc-desc {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem;
        color: #8B7355;
        margin: 0;
        line-height: 1.4;
        text-transform: capitalize;
    }

    /* ── Wiki card ── */
    .tm-wiki-card {
        background: linear-gradient(135deg,
            rgba(232,213,163,0.22), rgba(200,221,212,0.18));
        border: 1.5px solid rgba(201,169,110,0.25);
        border-radius: 18px;
        padding: 1.8rem 2rem;
        box-shadow: 0 4px 20px rgba(139,110,71,0.10);
        line-height: 1.75;
        font-family: 'Nunito', sans-serif;
        font-size: 0.95rem;
        color: #2C2416;
        animation: fadeUp 0.5s both;
    }

    /* ── Read more button ── */
    .tm-readmore .stLinkButton a {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        background: linear-gradient(135deg, #4A7C59, #2D5016) !important;
        color: #fff !important;
        border-radius: 12px !important;
        padding: 8px 22px !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(45,80,22,0.28) !important;
        transition: all 0.22s ease !important;
        text-decoration: none !important;
    }
    .tm-readmore .stLinkButton a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(45,80,22,0.36) !important;
    }

    /* ── Empty / error states ── */
    .tm-empty-state {
        text-align: center;
        padding: 2.4rem 1rem;
        border-radius: 18px;
        background: rgba(250,247,240,0.7);
        border: 1.5px dashed rgba(74,124,89,0.25);
    }
    .tm-empty-state .es-icon { font-size: 3rem; display: block; margin-bottom: 0.7rem; }
    .tm-empty-state p {
        font-family: 'Nunito', sans-serif;
        color: #8B7355;
        font-size: 0.92rem;
        margin: 0;
    }

    /* ── Divider ── */
    .tm-divider {
        border: none;
        height: 1.5px;
        background: linear-gradient(90deg, transparent, rgba(74,124,89,0.3), rgba(201,169,110,0.25), transparent);
        margin: 1.8rem 0;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # HERO
    # ============================================

    st.markdown("""
    <div class="tm-dest-hero">
        <div class="tm-dest-badge">🗺️ Destination Explorer</div>
        <h1>Destination Information</h1>
        <p>
            Discover real-time weather forecasts, stunning photo galleries,
            and rich destination insights — all in one place.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # SEARCH CARD
    # ============================================

    st.markdown("""
    <style>
    /* ── Input & Selectbox labels — BLACK, always visible ── */
    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p,
    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] label p {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* ── Placeholder text ── */
    [data-testid="stTextInput"] input::placeholder {
        color: #888070 !important;
        opacity: 1 !important;
        font-style: italic;
        font-size: 0.9rem;
    }

    /* ── Input typed text ── */
    [data-testid="stTextInput"] input {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.95rem !important;
        background: rgba(255,255,255,0.95) !important;
    }

    /* ── Selectbox selected value text ── */
    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.92rem !important;
    }

    /* ── Selectbox dropdown menu items ── */
    [data-baseweb="popover"] li {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
    }

    /* ── Button vertical alignment fix ── */
    .tm-explore-btn { padding-top: 1.82rem; }
    .tm-explore-btn .stButton > button { height: 2.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tm-search-outer">', unsafe_allow_html=True)
    st.markdown('<p class="tm-search-outer-label">🔍 Search Destination</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # NOTE: Columns must be OUTSIDE the HTML div — we style via CSS above
    col1, col2, col3 = st.columns([4, 2, 1], gap="medium")

    with col1:
        destination = st.text_input(
            "🌍 Destination",
            placeholder="e.g. Goa, Manali, Jaipur…",
        )
    with col2:
        forecast_days = st.selectbox(
            "📅 Forecast Days",
            [3, 5],
            index=1,
            format_func=lambda x: f"{x}-day forecast"
        )
    with col3:
        st.markdown('<div class="tm-explore-btn">', unsafe_allow_html=True)
        search_clicked = st.button("Explore 🌿", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================
    # RESULTS
    # ============================================

    if search_clicked:
        if not destination.strip():
            st.error("🌍 Please enter a destination name to continue.")
            return

        with st.spinner(f"Exploring {destination.title()}… 🌿"):

            images  = get_unsplash_image(destination, count=3, city=destination)
            weather = get_weather_forecast(destination, days=forecast_days)
            wiki    = get_wikipedia_summary(destination)

        # ── GALLERY ────────────────────────────
        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box green">📸</div>
            <div>
                <p class="sec-title">Photo Gallery</p>
                <p class="sec-sub">Curated images from Unsplash</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if images:
            g1, g2, g3 = st.columns(3, gap="small")
            for col, img in zip([g1, g2, g3], images):
                with col:
                    st.markdown(f'''
                    <div class="tm-photo-wrap">
                        <img src="{img["url"]}" style="width:100%; object-fit:cover; aspect-ratio:4/3; display:block;" />
                        <div class="tm-photo-overlay"></div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tm-empty-state">
                <span class="es-icon">🖼️</span>
                <p>No images found for this destination. Try a different spelling.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ── WEATHER ────────────────────────────
        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box blue">🌤️</div>
            <div>
                <p class="sec-title">Weather Forecast</p>
                <p class="sec-sub">Live data from OpenWeatherMap</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if weather:
            current = weather["current"]

            # Current conditions
            st.markdown('<div class="tm-weather-now">', unsafe_allow_html=True)
            st.markdown('<p class="tm-weather-label">Current Conditions</p>', unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("🌡️ Temperature", f"{current['temp']}°C")
            with m2:
                st.metric("💧 Humidity",    f"{current['humidity']}%")
            with m3:
                st.metric("💨 Wind Speed",  f"{current['wind_speed']} m/s")

            st.markdown('</div>', unsafe_allow_html=True)

            # Forecast strip
            st.markdown(f"**📅 {forecast_days}-Day Forecast**")
            fc_cols = st.columns(len(weather["forecast"]), gap="small")
            for idx, day in enumerate(weather["forecast"]):
                with fc_cols[idx]:
                    st.markdown(f"""
                    <div class="tm-forecast-card">
                        <p class="tm-fc-date">{day['date']}</p>
                        <p class="tm-fc-high">{day['temp_max']}°</p>
                        <p class="tm-fc-low">{day['temp_min']}°C</p>
                        <p class="tm-fc-desc">{day['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tm-empty-state">
                <span class="es-icon">⛅</span>
                <p>Weather data unavailable. Check your API key or try a different city.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ── WIKIPEDIA ──────────────────────────
        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box golden">📖</div>
            <div>
                <p class="sec-title">About the Destination</p>
                <p class="sec-sub">Sourced from Wikipedia</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if wiki and wiki.get("exists"):
            st.markdown(f'<div class="tm-wiki-card">{wiki["summary"]}</div>',
                        unsafe_allow_html=True)
            if wiki.get("url"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="tm-readmore">', unsafe_allow_html=True)
                st.link_button("📚 Read Full Article →", wiki["url"])
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tm-empty-state">
                <span class="es-icon">📖</span>
                <p>No Wikipedia article found. Try searching for the destination's full name.</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        # ── IDLE STATE ─────────────────────────
        st.markdown("""
        <div class="tm-empty-state" style="margin-top: 1rem; padding: 3.5rem 2rem;">
            <span class="es-icon">🧭</span>
            <p style="font-size:1.05rem; color:#4A7C59; font-weight:700; margin-bottom:0.5rem;">
                Enter a destination above to begin
            </p>
            <p>
                We'll fetch live weather, stunning photos,<br>
                and a rich travel guide — all in seconds.
            </p>
        </div>
        """, unsafe_allow_html=True)