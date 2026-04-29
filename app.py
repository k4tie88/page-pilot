import streamlit as st
import pandas as pd

st.set_page_config(page_title="ReadRoute 🧭")
st.title("🧭 ReadRoute")

uploaded_file = st.sidebar.file_uploader("Nahraj Goodreads CSV", type="csv")

if uploaded_file:
    try:
        # Načtení - latin1 a ošetření neviditelných znaků na začátku (utf-8-sig)
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='latin1')

        # OPRAVA: Vyčistíme názvy sloupců od všech nesmyslů
        df.columns = df.columns.str.strip().str.replace('"', '')

        # TADY JE TA MAGIE: 
        # Místo jména 'Exclusive Shelf' použijeme to, že je to 18. sloupec v pořadí
        # (v Pythonu se počítá od nuly, takže 17)
        shelf_col = df.columns[17] if len(df.columns) > 17 else None
        title_col = df.columns[1] if len(df.columns) > 1 else None
        author_col = df.columns[2] if len(df.columns) > 2 else None

        if shelf_col:
            # Chceme jen to, co není 'read' a 'did-not-finish'
            mask = ~df[shelf_col].str.lower().isin(['read', 'did-not-finish', 'currently-reading'])
            tbr = df[mask].copy()

            st.success(f"Načteno! Máš {len(tbr)} knih v pořadníku.")

            if not tbr.empty:
                if st.button("🎲 Doporuč mi něco!"):
                    book = tbr.sample(1).iloc[0]
                    st.divider()
                    st.subheader(f"📖 {book[title_col]}")
                    st.write(f"**Autor:** {book[author_col]}")
            else:
                st.warning("Seznam k přečtení je prázdný.")
        else:
            st.error("Soubor vypadá jinak, než čekám. Zkusila jsi exportovat přímo z Goodreads?")

    except Exception as e:
        st.error(f"Chyba: {e}")
else:
    st.info("Nahraj CSV soubor vlevo v menu.")
