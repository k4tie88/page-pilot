import streamlit as st
import pandas as pd
import random

# Konfigurace stránky
st.set_page_config(page_title="PagePilot", page_icon="📚", layout="wide")

# Vlastní CSS pro trochu "cool" vzhled
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 PagePilot")
st.subheader("Your personal book recommendation engine")

# Sidebar pro nahrání souboru
with st.sidebar:
    st.header("Data Source")
    uploaded_file = st.file_uploader("Upload Goodreads CSV", type="csv")
    st.info("Tip: Export your data from Goodreads Settings > Export.")

if uploaded_file:
    try:
        # Načtení dat
        df = pd.read_csv(uploaded_file)
        
        # Rozdělení na přečtené a k přečtení
        read_books = df[df['Exclusive Shelf'] == 'read']
        to_read_books = df[df['Exclusive Shelf'] == 'to-read']
        
        # Statistiky pro úvod
        col1, col2, col3 = st.columns(3)
        col1.metric("Finished Books", len(read_books))
        col2.metric("In To-Read List", len(to_read_books))
        col3.metric("Avg. Rating", round(read_books['My Rating'].replace(0, pd.NA).mean(), 2))

        st.divider()

        # SEKCE DOPORUČOVÁNÍ
        st.header("🎯 What's Next?")
        
        tab1, tab2, tab3 = st.tabs(["🎲 Random Pick", "🔥 Top Rated in TBR", "⏱️ Quick Read"])

        with tab1:
            if st.button("Surprise Me!"):
                if not to_read_books.empty:
                    book = to_read_books.sample(1).iloc[0]
                    st.balloons()
                    st.success(f"### {book['Title']}")
                    st.write(f"**Author:** {book['Author']}")
                    st.write(f"**Pages:** {book['Number of Pages']}")
                else:
                    st.warning("Your To-Read list is empty!")

        with tab2:
            st.write("Books in your To-Read list with the highest community rating (Average Rating):")
            # Goodreads má 'Average Rating' pro celou komunitu
            top_rated = to_read_books.sort_values(by='Average Rating', ascending=False).head(5)
            st.table(top_rated[['Title', 'Author', 'Average Rating']])

        with tab3:
            st.write("Shortest books from your wishlist:")
            short_books = to_read_books[to_read_books['Number of Pages'] > 0].sort_values(by='Number of Pages').head(5)
            st.table(short_books[['Title', 'Author', 'Number of Pages']])

        # BONUS: Analýza autora
        st.divider()
        st.header("📊 Your Favorite Authors")
        top_authors = read_books.groupby('Author')['My Rating'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(top_authors)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.image("https://images.unsplash.com/photo-1507842217343-583bb7270b66?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80")
    st.write("Please upload your `goodreads_library_export.csv` to start the magic.")