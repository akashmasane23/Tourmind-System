import streamlit as st
from utils.openai_chatbot import get_openai_response


def show():

    # ============================================
    # PAGE STYLES
    # ============================================

    st.markdown("""
    <style>
    /* ── Page header ── */
    .tm-chat-hero {
        background: linear-gradient(135deg,
            rgba(45,80,22,0.92) 0%,
            rgba(74,124,89,0.80) 55%,
            rgba(46,134,171,0.70) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(45,80,22,0.22);
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }

    .tm-chat-hero::after {
        content: "💬";
        position: absolute;
        right: 2.5rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 5rem;
        opacity: 0.12;
        pointer-events: none;
    }

    .tm-chat-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }

    .tm-chat-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        margin: 0;
        line-height: 1.6;
    }

    .tm-chat-hero .tm-chat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(244,185,66,0.22);
        border: 1px solid rgba(244,185,66,0.45);
        color: #F4B942;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        padding: 4px 14px;
        border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── Suggestion chips ── */
    .tm-chips-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 1rem 0 1.6rem;
        animation: fadeUp 0.6s 0.2s both;
    }

    .tm-chip {
        background: rgba(200,221,212,0.45);
        border: 1.5px solid rgba(74,124,89,0.28);
        color: #2D5016;
        font-family: 'Nunito', sans-serif;
        font-size: 0.84rem;
        font-weight: 600;
        padding: 7px 16px;
        border-radius: 99px;
        cursor: pointer;
        transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1);
        backdrop-filter: blur(6px);
        white-space: nowrap;
        user-select: none;
    }

    .tm-chip:hover {
        background: rgba(74,124,89,0.22);
        border-color: rgba(74,124,89,0.6);
        transform: translateY(-2px) scale(1.04);
        box-shadow: 0 4px 14px rgba(45,80,22,0.18);
    }

    /* ── Chat bubbles ── */
    [data-testid="stChatMessage"] {
        border-radius: 18px !important;
        margin-bottom: 0.6rem !important;
        animation: fadeUp 0.35s ease both;
    }

    /* Chat bubbles background override */
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"] {
        background: linear-gradient(135deg,
            rgba(250,247,240,0.95), rgba(232,213,163,0.15)) !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Chat bubbles text color force dark for perfect readability (targets every possible text tag inside chat containers) */
    [data-testid="stChatMessage"] *,
    [data-testid="stChatMessageContent"] *,
    .stChatMessage *,
    div[data-chat-message-role] *,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h5,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h6,
    div[data-chat-message-role] [data-testid="stMarkdownContainer"] *,
    div[data-chat-message-role] [data-testid="stMarkdownContainer"] p,
    div[data-chat-message-role] [data-testid="stMarkdownContainer"] span,
    div[data-chat-message-role] [data-testid="stMarkdownContainer"] li,
    div[data-chat-message-role] [data-testid="stMarkdownContainer"] strong,
    div[data-chat-message-role] [data-testid="stMarkdownContainer"] em {
        color: #1a1a1a !important;
    }

    /* Link styling inside bubbles - high specificity to override universal rule */
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] a,
    [data-testid="stChatMessageContent"] a,
    [data-testid="stChatMessage"] a,
    div[data-chat-message-role] a {
        color: #2E86AB !important;
        text-decoration: underline !important;
    }

    /* Code block styling inside bubbles - high specificity to override universal rule */
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] code,
    [data-testid="stChatMessageContent"] code,
    [data-testid="stChatMessage"] code,
    div[data-chat-message-role] code {
        color: #C0392B !important;
        background-color: rgba(0,0,0,0.05) !important;
    }

    /* ── Divider ── */
    .tm-chat-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.4rem 0 1rem;
    }

    .tm-chat-divider hr {
        flex: 1;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(74,124,89,0.3), transparent);
        margin: 0 !important;
    }

    .tm-chat-divider span {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #7AAE8E;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* ── Empty state ── */
    .tm-empty-chat {
        text-align: center;
        padding: 3rem 1rem;
        animation: fadeUp 0.5s 0.1s both;
    }

    .tm-empty-chat .tm-empty-icon {
        font-size: 4rem;
        display: block;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 12px rgba(74,124,89,0.3));
    }

    .tm-empty-chat h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #2D5016 !important;
        font-size: 1.4rem !important;
        margin-bottom: 0.5rem !important;
    }

    .tm-empty-chat p {
        font-family: 'Nunito', sans-serif;
        color: #8B7355;
        font-size: 0.92rem;
        max-width: 380px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Clear button override ── */
    .tm-clear-btn .stButton > button {
        background: linear-gradient(135deg,
            rgba(139,110,71,0.15), rgba(74,50,40,0.12)) !important;
        color: #8B6E47 !important;
        border: 1.5px solid rgba(139,110,71,0.3) !important;
        box-shadow: none !important;
        font-size: 0.88rem !important;
        height: 2.6em;
    }

    .tm-clear-btn .stButton > button:hover {
        background: linear-gradient(135deg,
            rgba(139,110,71,0.28), rgba(74,50,40,0.22)) !important;
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 4px 14px rgba(139,110,71,0.2) !important;
    }

    /* ── Chat input wrapper (the dark bar) ── */
    [data-testid="stChatInput"] {
        background: rgba(250,247,240,0.97) !important;
        border-top: 1.5px solid rgba(74,124,89,0.18) !important;
        padding: 10px 16px !important;
    }

    /* Bottom sticky bar — all layers */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div,
    [data-testid="stBottom"] > div > div > div,
    .stChatInput,
    section[data-testid="stBottom"] {
        background: rgba(240,237,228,0.98) !important;
        border-top: 1.5px solid rgba(74,124,89,0.20) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: none !important;
    }

    /* Kill any inherited dark backgrounds */
    [data-testid="stBottom"] * {
        background-color: transparent !important;
    }

    /* Re-apply white only to the textarea itself */
    [data-testid="stBottom"] textarea {
        background-color: #ffffff !important;
    }

    /* The textarea itself */
    [data-testid="stChatInput"] textarea {
        font-family: 'Nunito', sans-serif !important;
        border-radius: 14px !important;
        border: 1.5px solid rgba(74,124,89,0.30) !important;
        background: #ffffff !important;
        font-size: 0.95rem !important;
        color: #1a1a1a !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }

    /* Placeholder text — explicit light background contrast */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #7A6E5F !important;
        opacity: 1 !important;
        font-style: italic !important;
        font-size: 0.92rem !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #4A7C59 !important;
        box-shadow: 0 0 0 3px rgba(74,124,89,0.15) !important;
        outline: none !important;
    }

    /* Send arrow button */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #4A7C59, #2D5016) !important;
        border-radius: 10px !important;
        color: #fff !important;
        border: none !important;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #4A7C59 !important; }

    /* ── Stats bar ── */
    .tm-stats-bar {
        display: flex;
        gap: 1.2rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
        animation: fadeUp 0.5s 0.15s both;
    }

    .tm-stat-pill {
        background: rgba(200,221,212,0.4);
        border: 1px solid rgba(74,124,89,0.2);
        border-radius: 99px;
        padding: 5px 14px;
        font-family: 'Nunito', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: #4A7C59;
        backdrop-filter: blur(4px);
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # HERO HEADER
    # ============================================

    st.markdown("""
    <div class="tm-chat-hero">
        <div class="tm-chat-badge">🤖 AI Powered</div>
        <h1 style="color:#fff!important;font-family:'Playfair Display',Georgia,serif!important;">TourMind AI Chatbot</h1>
        <p style="color:rgba(255,255,255,0.88)!important;">
            Ask me about destinations, itineraries, budgets,<br>
            travel tips, or nearby attractions 🌍
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # CHAT MEMORY INITIALIZATION
    # ============================================

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ============================================
    # STATS BAR
    # ============================================

    msg_count = len(st.session_state.chat_history)
    user_msgs = msg_count // 2

    if msg_count > 0:
        st.markdown(f"""
        <div class="tm-stats-bar">
            <span class="tm-stat-pill">💬 {user_msgs} question{"s" if user_msgs != 1 else ""} asked</span>
            <span class="tm-stat-pill">🤖 {user_msgs} response{"s" if user_msgs != 1 else ""} generated</span>
        </div>
        """, unsafe_allow_html=True)

    # ============================================
    # SUGGESTION CHIPS (shown when chat is empty)
    # ============================================

    suggestions = [
        "🏖️ Best beaches in Goa",
        "🗓️ 5-day Kerala itinerary",
        "💰 Budget trip to Rajasthan",
        "🌄 Himachal Pradesh in winter",
        "🍜 Street food in Mumbai",
        "🏯 Hidden forts near Pune",
    ]

    if not st.session_state.chat_history:
        st.markdown("""
        <div class="tm-empty-chat">
            <span class="tm-empty-icon">🌿</span>
            <h3>Where do you want to explore?</h3>
            <p>Ask me anything about your next adventure — I'm your personal travel expert.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**✨ Try asking:**")
        st.markdown('<div class="tm-chips-wrap">' +
                    "".join(f'<span class="tm-chip">{s}</span>' for s in suggestions) +
                    '</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="tm-chat-divider">
            <hr><span>or type your own question below</span><hr>
        </div>
        """, unsafe_allow_html=True)

    # ============================================
    # DISPLAY CHAT HISTORY
    # ============================================

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)

    # ============================================
    # USER INPUT
    # ============================================

    user_input = st.chat_input("Ask about destinations, budgets, itineraries…")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("TourMind is exploring the world for you… 🌍"):
                response = get_openai_response(
                    user_input,
                    st.session_state.chat_history
                )
                st.markdown(response)

        st.session_state.chat_history.append(("user",      user_input))
        st.session_state.chat_history.append(("assistant", response))
        st.rerun()

    # ============================================
    # CLEAR CHAT BUTTON
    # ============================================

    if st.session_state.chat_history:
        st.markdown("---")
        col_clr, _ = st.columns([1, 4])
        with col_clr:
            st.markdown('<div class="tm-clear-btn">', unsafe_allow_html=True)
            if st.button("🗑️ Clear Conversation"):
                st.session_state.chat_history = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)