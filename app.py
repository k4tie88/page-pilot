import streamlit as st
import pandas as pd

st.set_page_config(page_title="ReadRoute 🧭", page_icon="📚")
st.title("🧭 ReadRoute")

# Funkce pro vyčištění ID (aby fungoval odkaz na web)
def clean_id(val):
    return str(val).replace('=', '').replace('"', '').strip()

uploaded_file = st.sidebar.file_uploader("Nahraj Goodreads CSV", type="csv")

if uploaded_file:
    try:
        # Načtení s ošetřením kódování (latin1 je pro GR export nejjistější)
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='latin1')

        # Vyčištění názvů sloupců (odstraní mezery a neviditelné znaky)
        df.columns = df.columns.str.strip().str.replace('"', '')

        # Dynamické určení sloupců podle pořadí (neprůstřelná metoda)
        title_col = next((c for c in df.columns if 'Title' in c), df.columns[1])
        author_col = next((c for c in df.columns if 'Author' in c and 'l-f' not in c), df.columns[2])
        shelf_col = next((c for c in df.columns if 'Shelf' in c), df.columns[17])
        id_col = 'Book Id'

        # FILTR: Nechceme 'read', 'did-not-finish' a to, co zrovna čteš
        forbidden = ['read', 'did-not-finish', 'currently-reading']
        tbr = df[~df[shelf_col].str.lower().isin(forbidden)].copy()

        st.success(f"Načteno! Máš {len(tbr)} knih k výběru.")

        if not tbr.empty:
            if st.button("🎲 Doporuč mi další knihu"):
                book = tbr.sample(1).iloc[0]
                
                # Vyčištění ID a vytvoření odkazu
                book_id = clean_id(book[id_col])
                gr_url = f"https://www.goodreads.com/book/show/{book_id}"
                
                st.divider()
                st.subheader(f"📖 {book[title_col]}")
                st.write(f"**Autor:** {book[author_col]}")
                
                # Odkaz přímo na Goodreads
                st.link_button("Otevřít na Goodreads ↗", gr_url)
                
                # Pokud jsou dostupné stránky, ukážeme je
                if 'Number of Pages' in book:
                    try:
                        pages = int(float(book['Number of Pages']))
                        if pages > 0:
                            st.caption(f"Délka: {pages} stran")
                    except:
                        pass
        else:
            st.warning("V seznamu To-Read nic nezbylo.")

    except Exception as e:
        st.error(f"Chyba při zpracování: {e}")
else:
    st.info("Nahraj CSV soubor z Goodreads v levém panelu.")
