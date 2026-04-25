"""
Peak Hours & Nearby Page — Travel/Nature Theme
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_handlers import load_peak_hours, get_place_peak_hours, load_places
from utils.realtime_places import get_nearby_attractions
from utils.realtime_crowd import predict_crowd_detail


# ============================================
# HELPER FUNCTIONS
# ============================================

def crowd_to_value(level):
    return {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}.get(level, 1)


def crowd_to_color(level):
    return {
        "Low":       ("#4A7C59", "#2D5016"),
        "Medium":    ("#C9A96E", "#8B6E47"),
        "High":      ("#E8845A", "#C0623C"),
        "Very High": ("#C0392B", "#922B21"),
    }.get(level, ("#4A7C59", "#2D5016"))


def crowd_to_emoji(level):
    return {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Very High": "🔴"}.get(level, "🟢")


def get_coordinates(place_name):
    df = load_places()
    if df.empty:
        return None, None
    result = df[df["place_name"].str.lower().str.contains(place_name.lower(), na=False)]
    if result.empty:
        return None, None
    row = result.iloc[0]
    return row["latitude"], row["longitude"]

def is_place_open(activity_type: str, hour: int) -> bool:
    from services.ml_service import _ACTIVITY_HOURS
    lo, hi = _ACTIVITY_HOURS.get(str(activity_type).lower(), (8, 20))
    return lo <= hour <= hi


# ============================================
# MAIN PAGE
# ============================================

def show():

    # ============================================
    # STYLES
    # ============================================

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Nunito:wght@400;600;700&display=swap');

    /* ── Hero ── */
    .tm-peak-hero {
        background: linear-gradient(135deg,
            rgba(46,134,171,0.88) 0%,
            rgba(45,80,22,0.82) 50%,
            rgba(139,110,71,0.78) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(46,134,171,0.20);
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }
    .tm-peak-hero::after {
        content: "⏰";
        position: absolute;
        right: 2.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 5.5rem;
        opacity: 0.10;
        pointer-events: none;
    }
    .tm-peak-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .tm-peak-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        margin: 0; line-height: 1.6;
    }
    .tm-peak-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(135,206,235,0.22);
        border: 1px solid rgba(135,206,235,0.45);
        color: #87CEEB;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 1.8px; text-transform: uppercase;
        padding: 4px 14px; border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── Search bar ── */
    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInput"] input {
        color: #1a1a1a !important;
        background: #fff !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.95rem !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(74,124,89,0.28) !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #999 !important; font-style: italic !important; opacity: 1 !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #4A7C59 !important;
        box-shadow: 0 0 0 3px rgba(74,124,89,0.15) !important;
    }

    /* ── Info cards row ── */
    .tm-info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0 1.4rem;
    }
    .tm-info-tile {
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        font-family: 'Nunito', sans-serif;
        backdrop-filter: blur(8px);
        box-shadow: 0 3px 14px rgba(44,36,22,0.09);
        transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.22s;
        animation: fadeUp 0.45s both;
    }
    .tm-info-tile:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(44,36,22,0.14); }
    .tm-info-tile .tile-label {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 1.4px;
        text-transform: uppercase; margin: 0 0 0.35rem; opacity: 0.75;
    }
    .tm-info-tile .tile-value {
        font-size: 0.95rem; font-weight: 700; margin: 0; line-height: 1.4;
    }

    .tm-tile-green  { background: linear-gradient(135deg, rgba(74,124,89,0.14), rgba(45,80,22,0.08));  border: 1.5px solid rgba(74,124,89,0.25); color: #2D5016; }
    .tm-tile-red    { background: linear-gradient(135deg, rgba(232,132,90,0.14), rgba(192,98,60,0.08)); border: 1.5px solid rgba(232,132,90,0.28); color: #C0623C; }
    .tm-tile-blue   { background: linear-gradient(135deg, rgba(46,134,171,0.14), rgba(26,95,122,0.08)); border: 1.5px solid rgba(46,134,171,0.25); color: #1A5F7A; }
    .tm-tile-golden { background: linear-gradient(135deg, rgba(244,185,66,0.14), rgba(201,169,110,0.08)); border: 1.5px solid rgba(244,185,66,0.28); color: #8B6E47; }

    /* ── Section header ── */
    .tm-sec-head {
        display: flex; align-items: center;
        gap: 0.75rem; margin: 1.8rem 0 1rem;
    }
    .tm-sec-head .icon-box {
        width: 40px; height: 40px; border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 14px rgba(45,80,22,0.22);
        flex-shrink: 0;
    }
    .tm-sec-head .sec-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.2rem; font-weight: 700;
        color: #2D5016; margin: 0;
    }
    .tm-sec-head .sec-sub {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem; color: #8B7355; margin: 2px 0 0;
    }

    /* ── Crowd meter ── */
    .tm-crowd-wrap {
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 18px rgba(44,36,22,0.09);
        backdrop-filter: blur(8px);
        animation: fadeUp 0.5s both;
    }
    .tm-crowd-label {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem; font-weight: 700;
        letter-spacing: 1.3px; text-transform: uppercase;
        margin: 0 0 0.6rem; opacity: 0.75;
    }
    .tm-crowd-row {
        display: flex; align-items: center; gap: 1rem;
    }
    .tm-crowd-bar-outer {
        flex: 1; height: 14px; border-radius: 99px;
        background: rgba(255,255,255,0.35);
        overflow: hidden;
    }
    .tm-crowd-bar-inner {
        height: 100%; border-radius: 99px;
        transition: width 0.8s cubic-bezier(0.34,1.2,0.64,1);
    }
    .tm-crowd-badge {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1rem; font-weight: 700;
        white-space: nowrap;
    }

    /* ── Recommendation card ── */
    .tm-rec-card {
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 0.8rem;
        display: flex; align-items: flex-start; gap: 1rem;
        box-shadow: 0 3px 14px rgba(44,36,22,0.09);
        backdrop-filter: blur(6px);
        animation: fadeUp 0.5s both;
        font-family: 'Nunito', sans-serif;
    }
    .tm-rec-card .rec-icon { font-size: 1.6rem; flex-shrink: 0; margin-top: 2px; }
    .tm-rec-card .rec-text { font-size: 0.92rem; line-height: 1.55; margin: 0; }
    .tm-rec-card .rec-text strong { font-size: 0.95rem; }
    .tm-rec-best  { background: linear-gradient(135deg, rgba(74,124,89,0.13), rgba(45,80,22,0.07));  border: 1.5px solid rgba(74,124,89,0.25);  color: #2D5016; }
    .tm-rec-avoid { background: linear-gradient(135deg, rgba(232,132,90,0.13), rgba(192,98,60,0.07)); border: 1.5px solid rgba(232,132,90,0.28); color: #8B3A1A; }

    /* ── Nearby attraction cards ── */
    .tm-nearby-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 4px 18px rgba(44,36,22,0.10);
        margin-bottom: 1rem;
        display: flex;
        gap: 0;
        transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s;
        animation: fadeUp 0.5s both;
    }
    .tm-nearby-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 32px rgba(44,36,22,0.16);
    }
    .tm-nearby-img {
        width: 140px; min-height: 130px;
        object-fit: cover; flex-shrink: 0;
    }
    .tm-nearby-body {
        padding: 1rem 1.2rem;
        display: flex; flex-direction: column; justify-content: center;
    }
    .tm-nearby-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.05rem; font-weight: 700;
        color: #2D5016; margin: 0 0 0.35rem;
    }
    .tm-nearby-rating {
        font-family: 'Nunito', sans-serif;
        font-size: 0.85rem; font-weight: 700;
        color: #C9A96E; margin: 0 0 0.25rem;
    }
    .tm-nearby-addr {
        font-family: 'Nunito', sans-serif;
        font-size: 0.82rem; color: #8B7355;
        margin: 0; line-height: 1.45;
    }

    /* ── Data table ── */
    .tm-table-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.16);
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px rgba(44,36,22,0.09);
        animation: fadeUp 0.5s both;
    }

    /* ── Divider ── */
    .tm-divider {
        border: none; height: 1.5px;
        background: linear-gradient(90deg, transparent, rgba(74,124,89,0.3), rgba(201,169,110,0.25), transparent);
        margin: 1.6rem 0;
    }

    /* ── Empty state ── */
    .tm-empty-state {
        text-align: center; padding: 2.5rem 1rem;
        border-radius: 18px;
        background: rgba(250,247,240,0.75);
        border: 1.5px dashed rgba(74,124,89,0.25);
    }
    .tm-empty-state .es-icon { font-size: 3rem; display: block; margin-bottom: 0.7rem; }
    .tm-empty-state p {
        font-family: 'Nunito', sans-serif;
        color: #8B7355; font-size: 0.92rem; margin: 0;
    }

    /* ── Stagger ── */
    .tm-nearby-card:nth-child(1) { animation-delay: 0.04s; }
    .tm-nearby-card:nth-child(2) { animation-delay: 0.09s; }
    .tm-nearby-card:nth-child(3) { animation-delay: 0.14s; }
    .tm-nearby-card:nth-child(4) { animation-delay: 0.19s; }
    .tm-nearby-card:nth-child(5) { animation-delay: 0.24s; }

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
    <div class="tm-peak-hero">
        <div class="tm-peak-badge">📍 Live Crowd Intelligence</div>
        <h1>Peak Hours & Nearby Attractions</h1>
        <p>
            Find the best times to visit, dodge the crowds,
            and discover hidden gems near any attraction.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # SEARCH
    # ============================================

    col_inp, col_btn = st.columns([5, 1], gap="small")
    with col_inp:
        place_search = st.text_input(
            "🔍 Search Place",
            placeholder="e.g. Shaniwar Wada, Aga Khan Palace…"
        )
    user_preference = "any"
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("Search 🔍", use_container_width=True)

    # ============================================
    # RESULTS
    # ============================================

    if search_clicked:
        if not place_search.strip():
            st.error("⚠️ Please enter a place name to search.")
            st.session_state["peak_search_query"] = None
        else:
            st.session_state["peak_search_query"] = place_search.strip()

    active_query = st.session_state.get("peak_search_query")
    if active_query:
        # Override place_search for downstream code so it uses the active query
        place_search = active_query 
        if True: # dummy block to preserve existing indentation
            info = get_place_peak_hours(active_query)

            if not info:
                st.markdown("""
                <div class="tm-empty-state">
                    <span class="es-icon">🗺️</span>
                    <p>No information found for this place.<br>
                    Try a different spelling or nearby landmark.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"✅ Showing results for: **{info['place']}**")

                # ── INFO TILES ──────────────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#4A7C59,#2D5016);">🕐</div>
                    <div>
                        <p class="sec-title">Visit Intelligence</p>
                        <p class="sec-sub">Timing & crowd overview</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="tm-info-grid">
                    <div class="tm-info-tile tm-tile-green">
                        <p class="tile-label">✅ Best Time to Visit</p>
                        <p class="tile-value">{info['best_time']}</p>
                    </div>
                    <div class="tm-info-tile tm-tile-red">
                        <p class="tile-label">❌ Avoid During</p>
                        <p class="tile-value">{info['avoid_time']}</p>
                    </div>
                    <div class="tm-info-tile tm-tile-blue">
                        <p class="tile-label">📅 Peak Season</p>
                        <p class="tile-value">{info['peak_season']}</p>
                    </div>
                    <div class="tm-info-tile tm-tile-golden">
                        <p class="tile-label">👥 Average Crowd</p>
                        <p class="tile-value">{crowd_to_emoji(info['average_crowd'])} {info['average_crowd']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

                # ── CROWD METERS ────────────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#2E86AB,#1A5F7A);">🌡️</div>
                    <div>
                        <p class="sec-title">Crowd Levels</p>
                        <p class="sec-sub">Average & live AI prediction</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Average crowd
                avg_val   = crowd_to_value(info["average_crowd"])
                avg_c1, avg_c2 = crowd_to_color(info["average_crowd"])
                avg_pct   = int((avg_val / 4) * 100)

                st.markdown(f"""
                <div class="tm-crowd-wrap" style="background:linear-gradient(135deg,{avg_c1}18,{avg_c2}0d); border:1.5px solid {avg_c1}44;">
                    <p class="tm-crowd-label" style="color:{avg_c1};">📊 Average Crowd Level</p>
                    <div class="tm-crowd-row">
                        <div class="tm-crowd-bar-outer">
                            <div class="tm-crowd-bar-inner"
                                 style="width:{avg_pct}%; background:linear-gradient(90deg,{avg_c1},{avg_c2});"></div>
                        </div>
                        <span class="tm-crowd-badge" style="color:{avg_c1};">
                            {crowd_to_emoji(info['average_crowd'])} {info['average_crowd']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Live crowd (hybrid: rule-based + ML)
                crowd_detail = predict_crowd_detail("Pune")
                live_level   = crowd_detail["level"]
                live_val     = crowd_to_value(live_level)
                live_c1, live_c2 = crowd_to_color(live_level)
                
                ml_pred_curr = crowd_detail.get("ml_prediction")
                gauge_val = crowd_to_value(ml_pred_curr) if ml_pred_curr else live_val
                gauge_color = crowd_to_color(ml_pred_curr)[0] if ml_pred_curr else live_c1
                gauge_label = ml_pred_curr if ml_pred_curr else live_level
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge",
                    value = gauge_val,
                    title = {'text': f"🔴 Live Crowd Status: {gauge_label}", 'font': {'size': 20, 'color': '#333333', 'family': 'Playfair Display'}},
                    gauge = {
                        'axis': {'range': [0, 4.5], 'tickwidth': 1, 'tickcolor': "#333333", 'tickmode': 'array', 'tickvals': [1, 2, 3, 4], 'ticktext': ['Low', 'Medium', 'High', 'Very High']},
                        'bar': {'color': gauge_color, 'thickness': 0.3},
                        'bgcolor': "rgba(255,255,255,0.05)",
                        'borderwidth': 0,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 1.5], 'color': "rgba(74,124,89,0.15)"},
                            {'range': [1.5, 2.5], 'color': "rgba(201,169,110,0.15)"},
                            {'range': [2.5, 3.5], 'color': "rgba(232,132,90,0.15)"},
                            {'range': [3.5, 4.5], 'color': "rgba(192,57,43,0.15)"}],
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#333333", 'family': "Nunito"}, height=280, margin=dict(l=20, r=20, t=50, b=20))
                
                st.plotly_chart(fig_gauge, use_container_width=True)

                # ── 1. PEAK HOUR TREND GRAPH & PIE CHART ──
                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#4A7C59,#2D5016);">📈</div>
                    <div>
                        <p class="sec-title">Today's Crowd Trends</p>
                        <p class="sec-sub">Best Time to Visit Today</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Generating hourly predictions..."):
                    hours = list(range(24))
                    rule_scores = []
                    ml_scores = []
                    rule_levels = []
                    
                    for h in hours:
                        dtl = predict_crowd_detail(city=place_search, hour=h)
                        rule_scores.append(dtl["score"])
                        rule_levels.append(dtl["level"])
                        
                        ml_pred_h = dtl.get("ml_prediction")
                        if ml_pred_h:
                            ml_scores.append(crowd_to_value(ml_pred_h))
                        else:
                            ml_scores.append(crowd_to_value(dtl["level"]))
                            
                    df_trend = pd.DataFrame({
                        "Hour": hours,
                        "Rule-Based Score": rule_scores,
                        "ML Crowd Level": ml_scores,
                        "Rule Level": rule_levels
                    })
                    
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(
                        x=df_trend["Hour"], y=df_trend["Rule-Based Score"],
                        mode="lines+markers", name="Rule Score",
                        line=dict(color="#E8845A", width=3)
                    ))
                    fig_trend.add_trace(go.Scatter(
                        x=df_trend["Hour"], y=df_trend["ML Crowd Level"],
                        mode="lines", name="ML Level (1-4)",
                        line=dict(color="#2E86AB", width=3, dash="dot")
                    ))
                    fig_trend.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Nunito", color="#333333"),
                        xaxis=dict(title="Hour of Day (0-23)", tickmode="linear", tick0=0, dtick=2, showgrid=False),
                        yaxis=dict(title="Crowd Score / Level", showgrid=True, gridcolor="rgba(0,0,0,0.1)"),
                        margin=dict(l=20, r=20, t=20, b=20),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                st.plotly_chart(fig_trend, use_container_width=True)



                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

                # ── SMART RECOMMENDATION ────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#C9A96E,#8B6E47);">🧭</div>
                    <div>
                        <p class="sec-title">Smart Recommendation</p>
                        <p class="sec-sub">When to go & when to skip</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="tm-rec-card tm-rec-best">
                    <span class="rec-icon">✅</span>
                    <p class="rec-text">
                        <strong>Best time to visit {info['place']}:</strong><br>
                        {info['best_time']} — you'll enjoy fewer crowds and a better experience.
                    </p>
                </div>
                <div class="tm-rec-card tm-rec-avoid">
                    <span class="rec-icon">⚠️</span>
                    <p class="rec-text">
                        <strong>Avoid visiting during:</strong><br>
                        {info['avoid_time']} — expect heavy footfall and longer wait times.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

                # ── 2. NEARBY ATTRACTIONS (ML Ranked List) ──
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#2E86AB,#1A5F7A);">📍</div>
                    <div>
                        <p class="sec-title">Nearby Attractions</p>
                        <p class="sec-sub">ML-ranked · Local DB + OpenStreetMap</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                lat, lng = get_coordinates(place_search)

                if lat and lng:
                    from datetime import datetime as _dt
                    nearby_places = get_nearby_attractions(
                        lat, lng,
                        user_hour=_dt.now().hour,
                        user_preference=user_preference if user_preference != "any" else "",
                    )

                    if nearby_places:
                        
                        st.markdown("<p style='font-size:0.95rem;font-weight:700;color:#2E86AB;margin-bottom:0.5rem;'>Interactive Attraction Map</p>", unsafe_allow_html=True)
                        map_lats = [lat]
                        map_lngs = [lng]
                        map_names = [f"⭐ {info['place']} (Searched)"]
                        map_colors = ["#E8845A"] # Orange for searched place
                        
                        current_hour = _dt.now().hour
                        for p in nearby_places:
                            map_lats.append(p.get("lat", lat))
                            map_lngs.append(p.get("lng", lng))
                            map_names.append(p["name"])
                            is_open = is_place_open(p.get("activity", ""), current_hour)
                            map_colors.append("#4A7C59" if is_open else "#C0392B")

                        df_map = pd.DataFrame({"lat": map_lats, "lon": map_lngs, "name": map_names, "color": map_colors})
                        fig_map = px.scatter_mapbox(
                            df_map, lat="lat", lon="lon", hover_name="name",
                            color="color", color_discrete_map="identity",
                            zoom=12, height=350
                        )
                        fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig_map, use_container_width=True)

                        for idx, p in enumerate(nearby_places, 1):
                            photo    = p.get("photo") or \
                                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300&q=80"
                            ml_score = p.get("ml_score", None)
                            ml_badge = ""
                            if ml_score is not None:
                                ml_badge = f'<span style="display:inline-block;margin-top:0.35rem;'\
                                           f'font-size:0.75rem;font-weight:700;'\
                                           f'color:#1A5F7A;background:rgba(46,134,171,0.12);'\
                                           f'border:1px solid rgba(46,134,171,0.25);'\
                                           f'border-radius:99px;padding:2px 10px;">'\
                                           f'✨ Smart Match: {int(ml_score * 100)}%</span>'
                                           
                            is_open = is_place_open(p.get('activity', ''), _dt.now().hour)
                            open_badge = f'<span style="display:inline-block;margin-top:0.35rem;margin-left:0.5rem;'\
                                         f'font-size:0.75rem;font-weight:700;'\
                                         f'color:{"#2D5016" if is_open else "#922B21"};'\
                                         f'background:{"rgba(74,124,89,0.15)" if is_open else "rgba(192,57,43,0.15)"};'\
                                         f'border:1px solid {"rgba(74,124,89,0.25)" if is_open else "rgba(192,57,43,0.25)"};'\
                                         f'border-radius:99px;padding:2px 10px;">'\
                                         f'{"🟢 OPEN NOW" if is_open else "🔴 CLOSED"}</span>'
                                         
                            rank_badge = f'<span style="display:inline-block;'\
                                         f'font-size:0.72rem;font-weight:700;color:#8B6E47;'\
                                         f'background:rgba(201,169,110,0.14);'\
                                         f'border:1px solid rgba(201,169,110,0.28);'\
                                         f'border-radius:99px;padding:2px 9px;margin-right:6px;">'\
                                         f'#{idx}</span>'
                            st.markdown(f"""
                            <div class="tm-nearby-card">
                                <img class="tm-nearby-img" src="{photo}" alt="{p['name']}">
                                <div class="tm-nearby-body">
                                    <p class="tm-nearby-name">{rank_badge}🗺️ {p['name']}</p>
                                    <p class="tm-nearby-rating">⭐ {p['rating']}</p>
                                    <p class="tm-nearby-addr">📍 {p['vicinity']} &nbsp;·&nbsp; {round(p.get('distance_km',0),1)} km</p>
                                    <div>{ml_badge}{open_badge}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)
                        st.markdown("""
                        <div class="tm-sec-head">
                            <div class="icon-box" style="background:linear-gradient(135deg,#9B59B6,#8E44AD);">✨</div>
                            <div>
                                <p class="sec-title">Smart Itinerary Generator</p>
                                <p class="sec-sub">Let AI plan your visits based on lowest crowd times</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Generate Smart Itinerary 🪄", use_container_width=True):
                            with st.spinner("Calculating optimal routing times..."):
                                st.markdown("<h4 style='color:#333333;'>Your Optimal Day Trip 📝</h4>", unsafe_allow_html=True)
                                curr_h = _dt.now().hour
                                visit_hour = max(9, curr_h + 1)
                                
                                for p in nearby_places[:4]:
                                    dtl = predict_crowd_detail(p['name'], hour=visit_hour)
                                    status = "🟢 Open" if is_place_open(p.get('activity',''), visit_hour) else "🔴 Closed"
                                    st.markdown(f"""
                                    <div style="padding:10px 15px; margin-bottom:10px; background:rgba(155,89,182,0.1); border-left:4px solid #8E44AD; border-radius:6px; font-family:'Nunito',sans-serif;">
                                        <span style="font-size:1.1rem; font-weight:700; color:#8E44AD;">🕒 {visit_hour:02d}:00</span> &nbsp;—&nbsp; Visit <strong>{p['name']}</strong><br>
                                        <span style="font-size:0.85em; color:#555;">Crowd Prediction: <strong>{dtl['level']}</strong> &nbsp;|&nbsp; Status: {status}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    visit_hour = (visit_hour + 2) % 24
                    else:
                        st.markdown("""
                        <div class="tm-empty-state">
                            <span class="es-icon">📍</span>
                            <p>No nearby attractions found in your area.<br>
                            Try increasing the search radius or a different location.</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="tm-empty-state">
                        <span class="es-icon">🌐</span>
                        <p>Coordinates not available for this place.<br>
                        Make sure it exists in your places dataset.</p>
                    </div>
                    """, unsafe_allow_html=True)


