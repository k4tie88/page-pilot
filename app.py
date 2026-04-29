import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="ReadRoute 🧭", layout="wide")

# Funkce, která vyčistí ty otravné =" " od Goodreads
def clean_val(val):
    if pd.isna(val): return ""
    return re.sub(r'[="]', '', str(val)).strip()

st.title("🧭 ReadRoute")
st.write("Nahraj export a já ti vyberu, co číst dál (vynechám přečtené).")

uploaded_file = st.sidebar.file_uploader("Upload Goodreads CSV", type="csv")

if uploaded_file:
    try:
        # Zkusíme načíst soubor (ošetření kódování)
        df = pd.read_csv(uploaded_file, encoding='latin1', on_bad_lines='skip')
        
        # 1. Vyčistíme názvy sloupců (odstraníme mezery)
        df.columns = [c.strip() for c in df.columns]
        
        # 2. Vyčistíme všechna data od =" " a uvozovek
        for col in df.columns:
            df[col] = df[col].apply(clean_val)

        # 3. Převedeme čísla, aby fungovalo řazení
        df['Number of Pages'] = pd.to_numeric(df['Number of Pages'], errors='coerce').fillna(0)
        df['Average Rating'] = pd.to_numeric(df['Average Rating'], errors='coerce').fillna(0)

        # 4. JEDNODUCHÝ FILTR (To, co jsi chtěla)
        # Chceme jen věci, které NEJSOU "read" a NEJSOU "did-not-finish"
        forbidden = ['read', 'did-not-finish']
        
        # Filtrujeme podle hlavního sloupce Exclusive Shelf
        tbr = df[~df['Exclusive Shelf'].str.lower().isin(forbidden)].copy()
        # Vyhodíme i "currently-reading", ať ti to nenabízí to, co zrovna držíš v ruce
        tbr = tbr[tbr['Exclusive Shelf'].str.lower() != 'currently-reading']

        st.success(f"Načteno! Máš {len(tbr)} knih k přečtení.")

        # DOPORUČOVÁK
        if not tbr.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎲 Náhodný tip"):
                    book = tbr.sample(1).iloc[0]
                    st.info(f"### {book['Title']}")
                    st.write(f"**Autor:** {book['Author']}")
                    st.write(f"**Stran:** {int(book['Number of Pages'])}")
                    # Odkaz na Goodreads (vyčištěné ID)
                    st.markdown(f"[Kouknout na Goodreads](https://www.goodreads.com/book/show/{book['Book Id']})")

            with col2:
                st.subheader("🔥 Nejlépe hodnocené (TBR)")
                top_books = tbr.sort_values(by='Average Rating', ascending=False).head(5)
                for i, row in top_books.iterrows():
                    st.write(f"⭐ {row['Average Rating']} - **{row['Title']}**")
        else:
            st.warning("V seznamu TBR nic nezbylo.")

    except Exception as e:
        st.error(f"Chyba: {e}")
