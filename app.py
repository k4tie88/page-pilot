import streamlit as st
import pandas as pd
import random
import re

# --- KONFIGURACE ---
st.set_page_config(page_title="ReadRoute 🧭", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }
    div.stButton > button { background-color: #ff4b4b; color: white; border-radius: 10px; font-weight: bold; width: 100%; }
    .book-card { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🧭 ReadRoute")
st.write("Your personal navigation through the world of books")

# --- POMOCNÉ FUNKCE PRO ČIŠTĚNÍ ---
def super_clean(val):
    """Odstraní =" " a uvozovky z jakékoliv hodnoty."""
    if pd.isna(val): return ""
    return re.sub(r'[="]', '', str(val)).strip()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload Goodreads CSV", type="csv")
    st.divider()
    max_pages = st.slider("Max pages", 50, 1500, 1500)
    st.caption("Filters active: Skipping read, DNF, and your personal blacklists.")

# --- LOGIKA ---
if uploaded_file:
    try:
        # Čteme CSV (vynutíme kódování a ošetříme chyby v řádcích)
        df = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='utf-8')
        
        # VYČIŠTĚNÍ CELÉHO DATAFRAMU (tady řešíme ty KeyError a uvozovky)
        # Uděláme kopii a vyčistíme názvy sloupců i data
        df.columns = [c.strip() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].apply(super_clean)

        # Převod důležitých sloupců na čísla
        df['Number of Pages'] = pd.to_numeric(df['Number of Pages'], errors='coerce').fillna(0)
        df['Average Rating'] = pd.to_numeric(df['Average Rating'], errors='coerce').fillna(0)
        df['My Rating'] = pd.to_numeric(df['My Rating'], errors='coerce').fillna(0)

        # ČERNÁ LISTINA
        blacklist = [
            'read', 'did-not-finish', 'author-to-avoid', 
            'not-appealing', 'never', 'checked-but-not-interested', 'currently-reading'
        ]

        # FILTROVÁNÍ
        def is_it_pickable(row):
            # 1. Kontrola hlavní poličky
            shelf = str(row.get('Exclusive Shelf', '')).lower()
            if shelf in blacklist or not shelf:
                return False
            
            # 2. Kontrola všech tagů v Bookshelves
            tags = str(row.get('Bookshelves', '')).lower()
            if any(b in tags for b in blacklist):
                return False
            
            return True

        # Vytvoření seznamu k doporučení
        tbr = df[df.apply(is_it_pickable, axis=1)].copy()
        
        # Filtr stránek
        if max_pages < 1500:
            tbr = tbr[tbr['Number of Pages'] <= max_pages]

        # STATS
        c1, c2, c3 = st.columns(3)
        c1.metric("Books in TBR", len(tbr))
        c2.metric("Total in CSV", len(df))
        c3.metric("Avg Community ⭐", f"{tbr['Average Rating'].mean():.2f}")

        st.divider()

        # ZÁLOŽKY S DOPORUČENÍM
        if not tbr.empty:
            tab1, tab2, tab3 = st.tabs(["🎲 Surprise Me", "🏆 Best Rated", "⚡ Short Reads"])

            with tab1:
                if st.button("Generate Random Recommendation"):
                    book = tbr.sample(1).iloc[0]
                    st.markdown(f"""
                    <div class="book-card">
                        <h3>{book['Title']}</h3>
                        <p><b>Author:</b> {book['Author']}<br>
                        <b>Pages:</b> {int(book['Number of Pages'])} | <b>Rating:</b> {book['Average Rating']} ⭐</p>
                        <a href="https://www.goodreads.com/book/show/{book['Book Id']}" target="_blank">View on Goodreads ↗</a>
                    </div>
                    """, unsafe_allow_html=True)

            with tab2:
                # Top 10 podle hodnocení a z nich náhodné 3
                top_selection = tbr.sort_values(by='Average Rating', ascending=False).head(10)
                random_top = top_selection.sample(min(3, len(top_selection)))
                for _, b in random_top.iterrows():
                    st.write(f"📖 **{b['Title']}** ({b['Average Rating']} ⭐)")
                    st.caption(f"by {b['Author']} | [Link](https://www.goodreads.com/book/show/{b['Book Id']})")
                    st.divider()

            with tab3:
                # Knihy s nejmenším počtem stran (ale víc než 0)
                shorts = tbr[tbr['Number of Pages'] > 0].sort_values(by='Number of Pages').head(10)
                if not shorts.empty:
                    random_shorts = shorts.sample(min(3, len(shorts)))
                    for _, b in random_shorts.iterrows():
                        st.write(f"⏱️ **{b['Title']}** ({int(b['Number of Pages'])} pages)")
                        st.caption(f"by {b['Author']} | [Link](https://www.goodreads.com/book/show/{b['Book Id']})")
                        st.divider()
        else:
            st.warning("No books found matching your criteria!")

    except Exception as e:
        st.error(f"Critical error: {e}")
        st.info("Try to re-download the CSV from Goodreads if the error persists.")
else:
    st.info("Please upload your Goodreads CSV to start.")
