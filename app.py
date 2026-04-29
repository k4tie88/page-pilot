import streamlit as st
import pandas as pd
import random
import re

# --- CONFIG ---
st.set_page_config(page_title="ReadRoute 🧭", page_icon="📚", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }
    div.stButton > button { background-color: #ff4b4b; color: white; border-radius: 10px; font-weight: bold; }
    .book-card { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧭 ReadRoute")
st.markdown("*Your personal navigation through the world of books*")

# --- HELPER FUNCTIONS ---
def clean_gr_id(val):
    """Odstraní =" " uvozovky, které Goodreads dává do exportu u ID."""
    if isinstance(val, str):
        return re.sub(r'[="]', '', val)
    return str(val)

# --- SIDEBAR ---
with st.sidebar:
    st.header("1. Data Source")
    uploaded_file = st.file_uploader("Upload Goodreads CSV", type="csv")
    st.divider()
    max_pages = st.slider("Max pages", 50, 1500, 1500)
    st.divider()
    st.caption("Auto-skipping: read, DNF, author-to-avoid, not-appealing, never, checked-but-not-interested.")

# --- MAIN LOGIC ---
if uploaded_file:
    try:
        # Načtení dat
        df = pd.read_csv(uploaded_file)
        
        # 1. ČIŠTĚNÍ DAT (Kritický krok)
        # Vyčištění Book Id (odstranění ="...")
        df['Book Id'] = df['Book Id'].apply(clean_gr_id)
        
        # Převod stránek na čísla (NaN nahradíme 0)
        df['Number of Pages'] = pd.to_numeric(df['Number of Pages'], errors='coerce').fillna(0)
        
        # 2. DEFINICE FILTRŮ
        blacklisted = [
            'read', 'did-not-finish', 'author-to-avoid', 
            'not-appealing', 'never', 'checked-but-not-interested'
        ]

        def is_available(row):
            # Kontrola hlavní poličky
            exc = str(row.get('Exclusive Shelf', '')).lower().strip()
            if exc in blacklisted or exc == 'currently-reading':
                return False
            
            # Kontrola tagů v Bookshelves
            shelves = str(row.get('Bookshelves', '')).lower()
            if any(tag in shelves for tag in blacklisted):
                return False
            
            return True

        # Vytvoření čistého TBR
        clean_tbr = df[df.apply(is_available, axis=1)].copy()
        
        # Aplikace filtru na počet stran
        if max_pages < 1500:
            clean_tbr = clean_tbr[clean_tbr['Number of Pages'] <= max_pages]

        # STATISTIKY
        m1, m2, m3 = st.columns(3)
        m1.metric("Available to Read", len(clean_tbr))
        m2.metric("Filtered Out", len(df) - len(clean_tbr))
        
        avg = df[df['Exclusive Shelf'] == 'read']['My Rating'].replace(0, pd.NA).mean()
        m3.metric("Your Avg Score", f"{avg:.2f} ⭐")

        st.divider()

        # --- SECTIONS ---
        if not clean_tbr.empty:
            t1, t2, t3 = st.tabs(["🎲 Random Selection", "🏆 Highest Rated", "⚡ Quick Reads"])

            with t1:
                if st.button("Roll the Dice! 🎲"):
                    book = clean_tbr.sample(1).iloc[0]
                    st.markdown(f"""
                    <div class="book-card">
                        <h3>{book['Title']}</h3>
                        <p><b>Author:</b> {book['Author']}<br>
                        <b>Length:</b> {int(book['Number of Pages'])} pages<br>
                        <b>Rating:</b> {book['Average Rating']} ⭐</p>
                        <a href="https://www.goodreads.com/book/show/{book['Book Id']}" target="_blank">View on Goodreads ↗</a>
                    </div>
                    """, unsafe_allow_html=True)

            with t2:
                st.write("Top 3 gems from your list:")
                top_3 = clean_tbr.sort_values(by='Average Rating', ascending=False).head(10).sample(min(3, len(clean_tbr)))
                for _, b in top_3.iterrows():
                    st.markdown(f"**{b['Title']}** ({b['Average Rating']} ⭐)  \n[Open link](https://www.goodreads.com/book/show/{b['Book Id']})")
                    st.divider()

            with t3:
                st.write("Books under 300 pages:")
                shorties = clean_tbr[clean_tbr['Number of Pages'] > 0].sort_values(by='Number of Pages').head(10)
                if not shorties.empty:
                    pick = shorties.sample(min(3, len(shorties)))
                    for _, b in pick.iterrows():
                        st.markdown(f"**{b['Title']}** - {int(b['Number of Pages'])} pages  \n[Open link](https://www.goodreads.com/book/show/{b['Book Id']})")
                else:
                    st.info("No short books found!")
        else:
            st.warning("No books found! Adjust the 'Max pages' slider or check your CSV labels.")

    except Exception as e:
        st.error(f"Logic Error: {e}")
        st.info("Check if your CSV has 'Book Id', 'Exclusive Shelf' and 'Title' columns.")
else:
    st.info("Awaiting your Goodreads CSV export...")
