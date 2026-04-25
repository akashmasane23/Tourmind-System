"""
Place Recommendations Page — Travel/Nature Theme
"""
import math
import pandas as pd
import streamlit as st
from utils.api_handlers import (
    get_unsplash_image,
    get_wikipedia_summary,
    get_google_maps_url
)
from utils.data_handlers import search_places
from config import DEFAULT_RESULTS_LIMIT


def show():

    # ============================================
    # STYLES
    # ============================================

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Nunito:wght@400;600;700&display=swap');

    /* ── Hero ── */
    .tm-places-hero {
        background: linear-gradient(135deg,
            rgba(45,80,22,0.90) 0%,
            rgba(74,124,89,0.82) 45%,
            rgba(46,134,171,0.75) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(45,80,22,0.22);
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }
    .tm-places-hero::after {
        content: "🏖️";
        position: absolute;
        right: 2.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 5.5rem;
        opacity: 0.10;
        pointer-events: none;
    }
    .tm-places-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important;
        border: none !important; padding: 0 !important;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .tm-places-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem; margin: 0; line-height: 1.6;
    }
    .tm-places-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(244,185,66,0.22);
        border: 1px solid rgba(244,185,66,0.45);
        color: #F4B942;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 1.8px; text-transform: uppercase;
        padding: 4px 14px; border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── All labels black ── */
    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p,
    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] label p {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    /* ── Inputs ── */
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

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #fff !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(74,124,89,0.28) !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSelectbox"] span { color: #1a1a1a !important; }

    /* ── Section header ── */
    .tm-sec-head {
        display: flex; align-items: center;
        gap: 0.75rem; margin: 1.8rem 0 1.2rem;
    }
    .tm-sec-head .icon-box {
        width: 42px; height: 42px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 14px rgba(45,80,22,0.22);
        flex-shrink: 0;
    }
    .tm-sec-head .sec-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.25rem; font-weight: 700;
        color: #2D5016; margin: 0;
    }
    .tm-sec-head .sec-sub {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem; color: #8B7355; margin: 2px 0 0;
    }

    /* ── Place card ── */
    .tm-place-card {
        background: rgba(250,247,240,0.95);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 4px 22px rgba(44,36,22,0.10);
        margin-bottom: 1.4rem;
        transition: transform 0.28s cubic-bezier(0.34,1.56,0.64,1),
                    box-shadow 0.28s ease,
                    border-color 0.25s ease;
        animation: fadeUp 0.55s both;
    }
    .tm-place-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 40px rgba(44,36,22,0.16);
        border-color: rgba(74,124,89,0.32);
    }
    .tm-place-card::before {
        content: "";
        display: block;
        height: 4px;
        background: linear-gradient(90deg, #4A7C59, #2E86AB, #C9A96E);
        border-radius: 22px 22px 0 0;
    }

    /* ── Card image column ── */
    .tm-card-img-wrap {
        position: relative;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(44,36,22,0.14);
    }
    .tm-card-img-wrap img { display: block; width: 100%; }
    .tm-card-img-overlay {
        position: absolute; inset: 0;
        background: linear-gradient(to top,
            rgba(45,80,22,0.6) 0%, transparent 55%);
        opacity: 0;
        transition: opacity 0.25s;
    }
    .tm-card-img-wrap:hover .tm-card-img-overlay { opacity: 1; }

    /* ── Photo credit ── */
    .tm-photo-credit {
        font-family: 'Nunito', sans-serif;
        font-size: 0.72rem; color: #8B7355;
        font-style: italic; margin: 0.4rem 0 0;
        text-align: center;
    }

    /* ── Place name ── */
    .tm-place-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.4rem; font-weight: 700;
        color: #2D5016; margin: 0 0 0.7rem;
        line-height: 1.2;
    }

    /* ── Meta pills ── */
    .tm-meta-row {
        display: flex; flex-wrap: wrap; gap: 8px;
        margin-bottom: 0.9rem;
    }
    .tm-meta-pill {
        display: inline-flex; align-items: center; gap: 5px;
        font-family: 'Nunito', sans-serif;
        font-size: 0.8rem; font-weight: 600;
        padding: 4px 12px; border-radius: 99px;
        white-space: nowrap;
    }
    .tm-pill-location {
        background: rgba(74,124,89,0.12);
        border: 1px solid rgba(74,124,89,0.28);
        color: #2D5016;
    }
    .tm-pill-keyword {
        background: rgba(201,169,110,0.14);
        border: 1px solid rgba(201,169,110,0.32);
        color: #8B6E47;
    }
    .tm-pill-activity {
        background: rgba(46,134,171,0.12);
        border: 1px solid rgba(46,134,171,0.28);
        color: #1A5F7A;
    }
    .tm-pill-coords {
        background: rgba(139,110,71,0.10);
        border: 1px solid rgba(139,110,71,0.22);
        color: #6B4F2A;
    }

    /* ── Wiki summary ── */
    .tm-wiki-snippet {
        font-family: 'Nunito', sans-serif;
        font-size: 0.9rem; color: #3A2E1E;
        line-height: 1.72; margin: 0.6rem 0 1rem;
        padding: 0.9rem 1.1rem;
        background: linear-gradient(135deg,
            rgba(232,213,163,0.18), rgba(200,221,212,0.14));
        border-left: 3px solid #4A7C59;
        border-radius: 0 12px 12px 0;
    }

    /* ── Link buttons ── */
    .tm-link-btn a {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 7px 18px !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        transition: all 0.22s ease !important;
        border: none !important;
        width: 100% !important;
        justify-content: center !important;
    }
    .tm-link-wiki a {
        background: linear-gradient(135deg, #4A7C59, #2D5016) !important;
        color: #fff !important;
        box-shadow: 0 3px 12px rgba(45,80,22,0.28) !important;
    }
    .tm-link-wiki a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(45,80,22,0.36) !important;
    }
    .tm-link-map a {
        background: linear-gradient(135deg, #2E86AB, #1A5F7A) !important;
        color: #fff !important;
        box-shadow: 0 3px 12px rgba(46,134,171,0.28) !important;
    }
    .tm-link-map a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(46,134,171,0.36) !important;
    }

    /* ── Result count badge ── */
    .tm-result-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg, rgba(74,124,89,0.14), rgba(45,80,22,0.08));
        border: 1.5px solid rgba(74,124,89,0.28);
        color: #2D5016;
        font-family: 'Nunito', sans-serif;
        font-size: 0.88rem; font-weight: 700;
        padding: 7px 18px; border-radius: 99px;
        margin-bottom: 1.4rem;
        animation: fadeUp 0.4s both;
    }

    /* ── Empty / error ── */
    .tm-empty-state {
        text-align: center; padding: 2.8rem 1rem;
        border-radius: 18px;
        background: rgba(250,247,240,0.75);
        border: 1.5px dashed rgba(74,124,89,0.25);
    }
    .tm-empty-state .es-icon { font-size: 3rem; display: block; margin-bottom: 0.7rem; }
    .tm-empty-state p {
        font-family: 'Nunito', sans-serif;
        color: #8B7355; font-size: 0.92rem; margin: 0;
    }

    /* ── Divider ── */
    .tm-divider {
        border: none; height: 1.5px;
        background: linear-gradient(90deg,
            transparent, rgba(74,124,89,0.3),
            rgba(201,169,110,0.25), transparent);
        margin: 0.8rem 0 1.6rem;
    }

    /* Stagger cards */
    .tm-place-card:nth-child(1)  { animation-delay: 0.03s; }
    .tm-place-card:nth-child(2)  { animation-delay: 0.08s; }
    .tm-place-card:nth-child(3)  { animation-delay: 0.13s; }
    .tm-place-card:nth-child(4)  { animation-delay: 0.18s; }
    .tm-place-card:nth-child(5)  { animation-delay: 0.23s; }
    .tm-place-card:nth-child(6)  { animation-delay: 0.28s; }
    .tm-place-card:nth-child(7)  { animation-delay: 0.33s; }
    .tm-place-card:nth-child(8)  { animation-delay: 0.38s; }
    .tm-place-card:nth-child(9)  { animation-delay: 0.43s; }
    .tm-place-card:nth-child(10) { animation-delay: 0.48s; }

    /* ── Number pills ── */
    .tm-count-pills {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 1.2rem;
        animation: fadeUp 0.4s 0.1s both;
    }
    .tm-count-label {
        font-family: 'Nunito', sans-serif;
        font-size: 0.82rem; font-weight: 700;
        color: #8B7355; letter-spacing: 0.5px;
        margin-right: 4px;
    }
    .tm-count-pill {
        font-family: 'Nunito', sans-serif;
        font-size: 0.84rem; font-weight: 700;
        padding: 5px 16px;
        border-radius: 99px;
        border: 1.5px solid rgba(74,124,89,0.28);
        background: rgba(200,221,212,0.35);
        color: #2D5016;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.34,1.56,0.64,1);
        user-select: none;
    }
    .tm-count-pill:hover {
        background: rgba(74,124,89,0.18);
        border-color: rgba(74,124,89,0.55);
        transform: translateY(-2px) scale(1.06);
        box-shadow: 0 4px 12px rgba(45,80,22,0.18);
    }
    .tm-count-pill.active {
        background: linear-gradient(135deg, #4A7C59, #2D5016);
        border-color: #2D5016;
        color: #fff;
        box-shadow: 0 4px 14px rgba(45,80,22,0.30);
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # HERO
    # ============================================

    st.markdown("""
    <div class="tm-places-hero">
        <div class="tm-places-badge">🌍 Destination Discovery</div>
        <h1>Tourist Place Recommendations</h1>
        <p>
            Explore stunning destinations with curated photos,
            rich Wikipedia insights, and instant Google Maps links.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # SEARCH BAR
    # ============================================

    # ── Extra CSS for filter bar ─────────────
    st.markdown("""
    <style>
    .tm-filter-bar {
        background: rgba(200,221,212,0.28);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 16px;
        padding: 1.2rem 1.4rem 0.8rem;
        margin-bottom: 1rem;
        animation: fadeUp 0.4s both;
    }
    .tm-sort-pills {
        display: flex; align-items: center;
        gap: 8px; flex-wrap: wrap;
        margin-top: 0.8rem;
    }
    .tm-sort-label {
        font-family: 'Nunito', sans-serif;
        font-size: 0.80rem; font-weight: 700;
        color: #8B7355; margin-right: 2px;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tm-sec-head">
        <div class="icon-box" style="background:linear-gradient(135deg,#4A7C59,#2D5016);">🔍</div>
        <div>
            <p class="sec-title">Search Destinations</p>
            <p class="sec-sub">Filter, sort and explore Pune's best places</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tm-filter-bar">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2.5, 2.5, 2, 1], gap="medium")
    with col1:
        city = st.text_input(
            "🏙️ City Name",
            placeholder="e.g. Pune, Mumbai…",
            key="city_search"
        )
    with col2:
        state = st.text_input(
            "🗺️ State Name",
            placeholder="e.g. Maharashtra, Goa…",
            key="state_search"
        )
    with col3:
        # Activity type filter
        activity_options = [
            "All", "historical", "religious", "nature", "spiritual",
            "adventure", "forts", "cultural", "shopping", "food",
            "family", "sports", "city"
        ]
        activity_filter = st.selectbox(
            "🎯 Activity Type",
            activity_options,
            key="activity_filter"
        )
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("Search 🔍", use_container_width=True, key="search_btn")

    # ── Sort pills ────────────────────────────
    st.markdown('<div class="tm-sort-pills"><span class="tm-sort-label">Sort by:</span>', unsafe_allow_html=True)

    SORT_OPTIONS = {
        "dist":  "📍 Distance",
        "alpha": "🔤 A → Z",
        "act":   "🎯 Activity",
        "rev_alpha": "🔤 Z → A",
    }
    # Initialise all session state keys once
    for _k, _v in [("sort_mode","dist"),("places_results",None),
                   ("places_query",""),("num_results",5)]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    sort_cols = st.columns(len(SORT_OPTIONS), gap="small")
    for i, (key_s, label) in enumerate(SORT_OPTIONS.items()):
        with sort_cols[i]:
            is_active = st.session_state.sort_mode == key_s
            if st.button(
                label,
                key=f"sort_{key_s}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.sort_mode = key_s
                # No st.rerun() — results re-sorted from session state on next render

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================
    # SEARCH LOGIC
    # ============================================

    # Pune city centre for distance calculation
    PUNE_LAT, PUNE_LNG = 18.5204, 73.8567

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)

    def add_distances(df):
        """Pre-compute distance_km from Pune centre for every row."""
        if "latitude" in df.columns and "longitude" in df.columns:
            df = df.copy()
            df["distance_km"] = df.apply(
                lambda r: haversine_km(PUNE_LAT, PUNE_LNG, r["latitude"], r["longitude"]),
                axis=1
            )
        return df

    def apply_sort(df, mode):
        if "latitude" in df.columns and "longitude" in df.columns:
            df = df.copy()
            df["distance_km"] = df.apply(
                lambda r: haversine_km(PUNE_LAT, PUNE_LNG, r["latitude"], r["longitude"]), axis=1
            )
        if mode == "dist" and "distance_km" in df.columns:
            return df.sort_values("distance_km")
        elif mode == "alpha":
            return df.sort_values("place_name")
        elif mode == "rev_alpha":
            return df.sort_values("place_name", ascending=False)
        elif mode == "act" and "activity_type" in df.columns:
            return df.sort_values(["activity_type", "place_name"])
        return df

    # ── Run search — store raw results in session_state ──────
    if search_clicked:
        if not city and not state and (not activity_filter or activity_filter == "All"):
            st.error("⚠️ Please enter at least a City, State, or select an Activity Type.")
        else:
            query_label = " · ".join(filter(None, [
                city.strip() if city else "",
                state.strip() if state else "",
                activity_filter if activity_filter != "All" else "",
            ]))
            with st.spinner(f"Discovering places in {query_label or 'Pune'}… 🌿"):
                raw_df = search_places(
                    city=city.strip() if city else None,
                    state=state.strip() if state else None,
                    activity_type=activity_filter if activity_filter != "All" else None,
                )
            if raw_df.empty:
                st.session_state["places_results"] = None
                st.markdown("""
                <div class="tm-empty-state">
                    <span class="es-icon">🗺️</span>
                    <p>No places found. Try a different city, state, or activity type.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Store with distances pre-computed
                st.session_state["places_results"] = add_distances(raw_df)
                st.session_state["places_query"]   = query_label or "Pune"

    # ── Render from session_state (survives ALL reruns / pill clicks) ──
    if st.session_state.get("places_results") is not None:
        places_df = apply_sort(
            st.session_state["places_results"],
            st.session_state.sort_mode
        )
        total = len(places_df)

        # ── Number pills ──────────────────────
        if "num_results" not in st.session_state:
            st.session_state.num_results = 5

        pill_options = [5, 10, 15, 20, total]
        pill_labels  = ["5", "10", "15", "20", "All"]

        st.markdown(f"""
        <div class="tm-result-badge">
            ✅ Found <strong>{total}</strong> place{"s" if total != 1 else ""}
            &nbsp;·&nbsp; Showing top <strong>{min(st.session_state.num_results, total)}</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="tm-count-pills"><span class="tm-count-label">Show:</span>', unsafe_allow_html=True)
        pill_cols = st.columns(len(pill_options), gap="small")
        for i, (val, label) in enumerate(zip(pill_options, pill_labels)):
            with pill_cols[i]:
                if st.button(label, key=f"pill_{val}", use_container_width=True,
                             type="primary" if st.session_state.num_results == val else "secondary"):
                    st.session_state.num_results = val
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        num_results = st.session_state.num_results

        # ============================================
        # ============================================
        # PREFETCH images + wiki IN PARALLEL
        # ============================================

        subset = places_df.head(num_results)
        names  = subset["place_name"].tolist()

        @st.cache_data(show_spinner=False)
        def _fetch_place_data(name, activity, city):
            imgs = get_unsplash_image(name, count=1, activity_type=activity, city=city)
            wiki = get_wikipedia_summary(name)
            return imgs, wiki

        prefetch = {}
        with st.spinner("Loading place details… 🌿"):
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=6) as pool:
                futs = {
                    pool.submit(
                        _fetch_place_data,
                        row["place_name"],
                        row.get("activity_type",""),
                        row.get("city","")
                    ): row["place_name"]
                    for _, row in subset.iterrows()
                }
                for fut in as_completed(futs):
                    n = futs[fut]
                    try:
                        prefetch[n] = fut.result()
                    except Exception:
                        prefetch[n] = ([], None)

        # ============================================
        # PLACE CARDS  (data already prefetched)
        # ============================================

        for idx, row in subset.iterrows():
            images, wiki_info = prefetch.get(row["place_name"], ([], None))

            st.markdown('<div class="tm-place-card">', unsafe_allow_html=True)
            inner_col_img, inner_col_info = st.columns([1, 2], gap="medium")

            with inner_col_img:
                st.markdown("<br>", unsafe_allow_html=True)
                if images:
                    st.markdown('<div class="tm-card-img-wrap">', unsafe_allow_html=True)
                    st.image(images[0]["url"], width='stretch')
                    st.markdown('<div class="tm-card-img-overlay"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<p class="tm-photo-credit">📸 Photo by {images[0]["photographer"]}</p>',
                        unsafe_allow_html=True
                    )
                else:
                    placeholders = [
                        "https://images.unsplash.com/photo-1506461883276-594a12b11ea3?q=80&w=800",
                        "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=800",
                        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=800",
                        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=800",
                        "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?q=80&w=800"
                    ]
                    seed = abs(hash(row["place_name"])) % len(placeholders)
                    st.image(placeholders[seed], width='stretch')

            with inner_col_info:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Rating logic
                rating = float(row.get("rating", 4.2)) if not pd.isna(row.get("rating", 4.2)) else 4.2
                stars = "★" * int(rating) + "☆" * (5 - int(rating))
                
                st.markdown(
                    f'<p class="tm-place-name">{row["place_name"]} <span style="font-size:1.1rem; color:#F4B942;">{stars}</span> <span style="font-size:0.9rem; color:#666;">({rating})</span></p>',
                    unsafe_allow_html=True
                )
                st.markdown(f"""
                <div class="tm-meta-row">
                    <span class="tm-meta-pill tm-pill-location">📍 {row['city']}, {row['state']}</span>
                    <span class="tm-meta-pill tm-pill-keyword">🏷️ {row['description_keyword']}</span>
                    <span class="tm-meta-pill tm-pill-activity">🎯 {row['activity_type']}</span>
                    <span class="tm-meta-pill" style="background:rgba(45,80,22,0.1); border:1px solid rgba(45,80,22,0.3); color:#2D5016;">🟢 Open Now</span>
                </div>
                """, unsafe_allow_html=True)

                try:
                    dist = float(row.get("distance_km", float("nan")))
                    if not math.isnan(dist):
                        dc = "#4A7C59" if dist <= 5 else "#C9A96E" if dist <= 20 else "#2E86AB"
                        st.markdown(f'''
                        <div style="display:inline-flex;align-items:center;gap:6px;
                                    background:{dc}14;border:1.5px solid {dc}44;
                                    border-radius:99px;padding:4px 14px;margin-bottom:0.7rem;">
                            <span style="font-family:Nunito,sans-serif;font-size:0.8rem;
                                         font-weight:700;color:{dc};">
                                📍 {dist} km from Pune centre
                            </span>
                        </div>''', unsafe_allow_html=True)
                except Exception:
                    pass

                if wiki_info and wiki_info.get("summary"):
                    snippet = wiki_info["summary"]
                    if len(snippet) > 280:
                        snippet = snippet[:280].rsplit(" ", 1)[0] + "…"
                    st.markdown(f'<p class="tm-wiki-snippet">{snippet}</p>', unsafe_allow_html=True)

                btn_c1, btn_c2 = st.columns(2, gap="small")
                with btn_c1:
                    if wiki_info and wiki_info.get("url"):
                        st.markdown('<div class="tm-link-btn tm-link-wiki">', unsafe_allow_html=True)
                        st.link_button("📖 Read More", wiki_info["url"], use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                with btn_c2:
                    st.markdown('<div class="tm-link-btn tm-link-map">', unsafe_allow_html=True)
                    st.link_button("🗺️ View on Map", get_google_maps_url(row["place_name"]), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)


    elif not search_clicked and not st.session_state.get("places_results"):
        st.markdown("""
        <div class="tm-empty-state" style="margin-top:1rem; padding:3.5rem 2rem;">
            <span class="es-icon">🧭</span>
            <p style="font-size:1.05rem; color:#4A7C59; font-weight:700; margin-bottom:0.5rem;">
                Start exploring destinations above
            </p>
            <p>Enter a city or state name, pick an activity type,<br>
            then hit Search to discover curated tourist spots.</p>
        </div>
        """, unsafe_allow_html=True)