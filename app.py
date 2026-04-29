import streamlit as st
import pandas as pd
import random
import re

# --- KONFIGURACE ---
st.set_page_config(page_title="ReadRoute 🧭", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }
    div.stButton > button { background-color: #ff4b4b; color: white; border-radius: 10px; font-weight: bold; }
    .book-card { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧭 ReadRoute")

# --- POMOCNÉ FUNKCE ---
def super_clean(val):
    if pd.isna(val): return ""
    return re.sub(r'[="]', '', str(val)).strip()

def load_data(file):
    # Zkusíme nejčastější kódování, které CSV používají
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            file.seek(0) # Reset streamu
            return pd.read_csv(file, encoding=encoding, on_bad_lines='skip')
        except UnicodeDecodeError:
            continue
    return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload Goodreads CSV", type="csv")
    st.divider()
    max_pages = st.slider("Max pages", 50, 1500, 1500)

# --- LOGIKA ---
if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        try:
            # Vyčištění názvů sloupců (mezery)
            df.columns = [c.strip() for c in df.columns]
            
            # Plošné vyčištění všech dat od =" "
            for col in df.columns:
                df[col] = df[col].apply(super_clean)

            # Převod čísel
            df['Number of Pages'] = pd.to_numeric(df['Number of Pages'], errors='coerce').fillna(0)
            df['Average Rating'] = pd.to_numeric(df['Average Rating'], errors='coerce').fillna(0)

            # Definice černé listiny
            blacklist = [
                'read', 'did-not-finish', 'author-to-avoid', 
                'not-appealing', 'never', 'checked-but-not-interested', 'currently-reading'
            ]

            # Filtrování (používáme .get() kvůli bezpečnosti názvů)
            def is_it_pickable(row):
                # Exclusive Shelf (opraven překlep v kódu)
                shelf = str(row.get('Exclusive Shelf', '')).lower()
                if shelf in blacklist or not shelf:
                    return False
                # Bookshelves tagy
                tags = str(row.get('Bookshelves', '')).lower()
                if any(b in tags for b in blacklist):
                    return False
                return True

            tbr = df[df.apply(is_it_pickable, axis=1)].copy()
            
            if max_pages < 1500:
                tbr = tbr[tbr['Number of Pages'] <= max_pages]

            # UI - Sekce
            st.success(f"Successfully loaded! {len(tbr)} books ready for recommendation.")
            
            tab1, tab2, tab3 = st.tabs(["🎲 Random Pick", "🏆 Top Rated", "⏱️ Quick Reads"])

            with tab1:
                if st.button("Generate Next Read"):
                    if not tbr.empty:
                        book = tbr.sample(1).iloc[0]
                        st.markdown(f"""
                        <div class="book-card">
                            <h3>{book['Title']}</h3>
                            <p><b>Author:</b> {book['Author']}<br>
                            <b>Pages:</b> {int(book['Number of Pages'])} | <b>Rating:</b> {book['Average Rating']} ⭐</p>
                            <a href="https://www.goodreads.com/book/show/{book['Book Id']}" target="_blank">View on Goodreads ↗</a>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("No books found.")

            with tab2:
                top_3 = tbr.sort_values(by='Average Rating', ascending=False).head(10)
                if not top_3.empty:
                    for _, b in top_3.sample(min(3, len(top_3))).iterrows():
                        st.write(f"📖 **{b['Title']}** ({b['Average Rating']} ⭐)")
                        st.caption(f"by {b['Author']} | [Goodreads](https://www.goodreads.com/book/show/{b['Book Id']})")
                        st.divider()

            with tab3:
                shorts = tbr[tbr['Number of Pages'] > 0].sort_values(by='Number of Pages').head(10)
                if not shorts.empty:
                    for _, b in shorts.sample(min(3, len(shorts))).iterrows():
                        st.write(f"⏱️ **{b['Title']}** ({int(b['Number of Pages'])} pages)")
                        st.caption(f"by {b['Author']} | [Goodreads](https://www.goodreads.com/book/show/{b['Book Id']})")
                        st.divider()

        except Exception as e:
            st.error(f"Error processing columns: {e}")
    else:
        st.error("Could not decode CSV. Please try to export it again from Goodreads.")
else:
    st.info("Upload your Goodreads export (CSV) to start.")
