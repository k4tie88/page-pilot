import streamlit as st
import pandas as pd
import random
import re

# Nastavení stránky
st.set_page_config(page_title="ReadRoute 🧭", page_icon="📚")

# Funkce pro vyčištění textu (odstraní =" a uvozovky)
def clean_gr_logic(val):
    if pd.isna(val): return ""
    return re.sub(r'[="]', '', str(val)).strip()

st.title("🧭 ReadRoute")
st.markdown("### Your simple book navigator")

# Nahrávání souboru v sidebaru
uploaded_file = st.sidebar.file_uploader("Upload Goodreads CSV", type="csv")

if uploaded_file:
    try:
        # Načtení s ignorováním špatného kódování (řeší ty čtverečky)
        df = pd.read_csv(uploaded_file, encoding='latin1', on_bad_lines='skip')
        
        # Srovnání názvů sloupců (odstraní mezery a opraví překlepy)
        df.columns = [c.strip() for c in df.columns]
        
        # Vyčištění dat od =" "
        for col in df.columns:
            df[col] = df[col].apply(clean_gr_logic)

        # Převod na čísla pro správné fungování
        df['Number of Pages'] = pd.to_numeric(df['Number of Pages'], errors='coerce').fillna(0)
        df['Average Rating'] = pd.to_numeric(df['Average Rating'], errors='coerce').fillna(0)

        # --- JEDNODUCHÝ FILTR ---
        # Definujeme, co nechceme vidět
        stop_list = ['read', 'did-not-finish', 'currently-reading']
        
        # Vyfiltrujeme TBR (To Be Read)
        # Používáme .str.lower(), aby to bylo imunní vůči velkým písmenům
        tbr = df[~df['Exclusive Shelf'].str.lower().isin(stop_list)].copy()

        st.success(f"Found {len(tbr)} books you haven't read yet!")

        # --- DOPORUČOVACÍ SEKCE ---
        if not tbr.empty:
            tab1, tab2 = st.tabs(["🎲 Random Pick", "🏆 Best Rated"])

            with tab1:
                if st.button("Give me a random book!"):
                    book = tbr.sample(1).iloc[0]
                    st.divider()
                    st.subheader(book['Title'])
                    st.write(f"**Author:** {book['Author']}")
                    st.write(f"**Pages:** {int(book['Number of Pages'])}")
                    st.markdown(f"[View on Goodreads](https://www.goodreads.com/book/show/{book['Book Id']})")

            with tab2:
                st.write("Highest rated by community:")
                top_3 = tbr.sort_values(by='Average Rating', ascending=False).head(3)
                for _, b in top_3.iterrows():
                    st.write(f"⭐ {b['Average Rating']} - **{b['Title']}** ({b['Author']})")
        else:
            st.warning("No books found in your To-Read list.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.info("Make sure you are uploading the original Goodreads CSV export.")
else:
    st.info("Waiting for your Goodreads CSV file...")
