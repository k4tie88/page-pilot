import streamlit as st
import pandas as pd
import random

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="ReadRoute 🧭",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VLASTNÍ STYLOVÁNÍ (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HLAVIČKA ---
st.title("🧭 ReadRoute")
st.markdown("*Your personal navigation through the world of books*")

# --- SIDEBAR S NAHRÁVÁNÍM ---
with st.sidebar:
    st.header("1. Data Source")
    uploaded_file = st.file_uploader("Upload Goodreads CSV", type="csv")
    
    st.divider()
    st.header("2. Navigation Settings")
    max_pages = st.slider("Max pages", 0, 1500, 1500)
    
    st.divider()
    st.info("I will automatically skip books you've read or marked as: 'did-not-finish', 'author-to-avoid', 'not-appealing', 'never', 'checked-but-not-interested'.")

# --- HLAVNÍ LOGIKA ---
if uploaded_file:
    try:
        # Načtení dat
        df = pd.read_csv(uploaded_file)

        # ČERNÁ LISTINA (tvůj požadavek)
        blacklisted = [
            'read', 'did-not-finish', 'author-to-avoid', 
            'not-appealing', 'never', 'checked-but-not-interested'
        ]

        # Funkce pro vyčištění TBR (To-Be-Read) listu
        def is_available(row):
            # Kontrola hlavní poličky
            exc = str(row.get('Exclusive Shelf', '')).lower()
            if exc in blacklisted or exc == 'currently-reading':
                return False
            
            # Kontrola všech tagů/poliček
            shelves = str(row.get('Bookshelves', '')).lower()
            if any(tag in shelves for tag in blacklisted):
                return False
            
            return True

        # Vytvoření "čistého" seznamu pro doporučení
        clean_tbr = df[df.apply(is_available, axis=1)].copy()
        
        # Filtr podle počtu stran (ošetření NaN hodnot)
        clean_tbr['Number of Pages'] = pd.to_numeric(clean_tbr['Number of Pages'], errors='coerce').fillna(0)
        if max_pages < 1500:
            clean_tbr = clean_tbr[clean_tbr['Number of Pages'] <= max_pages]

        # STATISTIKY
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Read & Ignored", len(df) - len(clean_tbr))
        with col2:
            st.metric("Ready to Recommend", len(clean_tbr))
        with col3:
            avg_rating = df[df['Exclusive Shelf'] == 'read']['My Rating'].replace(0, pd.NA).mean()
            st.metric("Your Avg Rating", f"{avg_rating:.2f} ⭐")

        st.divider()

        # SEKCE DOPORUČENÍ
        st.header("📖 What should you read next?")

        if not clean_tbr.empty:
            tab1, tab2, tab3 = st.tabs(["🎲 Random Pick", "💎 Community Gems", "⏱️ Quick Picks"])

            with tab1:
                st.write("Click the button to get a random suggestion from your TBR.")
                if st.button("Surprise Me!"):
                    book = clean_tbr.sample(1).iloc[0]
                    st.success(f"### {book['Title']}")
                    st.write(f"**Author:** {book['Author']}")
                    st.write(f"**Pages:** {int(book['Number of Pages'])}")
                    st.write(f"**Community Rating:** {book['Average Rating']} ⭐")
                    st.markdown(f"[Go to Goodreads](https://www.goodreads.com/book/show/{book['Book Id']})")

            with tab2:
                st.write("Top-rated books by the community (randomly selected from your Top 10).")
                top_10 = clean_tbr.sort_values(by='Average Rating', ascending=False).head(10)
                if not top_10.empty:
                    display_top = top_10.sample(min(3, len(top_10)))
                    for _, b in display_top.iterrows():
                        st.info(f"**{b['Title']}** by {b['Author']} ({b['Average Rating']} ⭐)")

            with tab3:
                st.write("Shorter books for a quick reading session.")
                short_ones = clean_tbr[clean_tbr['Number of Pages'] >
