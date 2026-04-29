# --- LOGIKA FILTROVÁNÍ (Tady se děje to kouzlo) ---

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        
        # 1. Definujeme seznam "zakázaných" poliček
        # Přidáme tam vše, co jsi psala + automaticky 'read'
        blacklisted_shelves = [
            'read', 
            'did-not-finish', 
            'author-to-avoid', 
            'not-appealing', 
            'never', 
            'checked-but-not-interested'
        ]

        # 2. Vytvoříme čistý seznam k doporučení (Clean TBR)
        # Musíme zkontrolovat 'Exclusive Shelf' i sloupec 'Bookshelves'
        
        def is_book_ok(row):
            # Kontrola hlavní poličky
            if row['Exclusive Shelf'] in blacklisted_shelves:
                return False
            
            # Kontrola tagů (Bookshelves může obsahovat více hodnot oddělených čárkou)
            if pd.notna(row['Bookshelves']):
                tags = [t.strip() for t in str(row['Bookshelves']).split(',')]
                if any(tag in blacklisted_shelves for tag in tags):
                    return False
            return True

        # Aplikujeme filtr
        potential_reads = df[df.apply(is_book_ok, axis=1)].copy()
        
        # Pro jistotu ještě vyhodíme vše, co máš v 'currently-reading' (pokud chceš fakt jen nové)
        potential_reads = potential_reads[potential_reads['Exclusive Shelf'] != 'currently-reading']

        # Statistiky pro ověření
        read_count = len(df[df['Exclusive Shelf'] == 'read'])
        st.write(f"✅ Ignored {len(df) - len(potential_reads)} books (read or blacklisted).")
        st.write(f"🎯 Available for recommendation: {len(potential_reads)} books.")

        st.divider()

        # --- SEKCE DOPORUČOVÁNÍ (What's Next?) ---
        st.header("📍 Find Your Next Destination")
        
        if not potential_reads.empty:
            tab1, tab2, tab3 = st.tabs(["🎲 Random Pick", "🔥 Community Gems", "⏱️ Quick Reads"])

            with tab1:
                if st.button("Surprise Me!"):
                    # Tady je to "pokaždé jinak" - bereme náhodný vzorek
                    book = potential_reads.sample(1).iloc[0]
                    st.success(f"### {book['Title']}")
                    st.write(f"**By {book['Author']}**")
                    st.caption(f"Pages: {book['Number of Pages']} | Avg Rating: {book['Average Rating']}")
                    st.markdown(f"[Open on Goodreads](https://www.goodreads.com/book/show/{book['Book Id']})")

            with tab2:
                st.write("Top rated books from your TBR list:")
                # Vybereme 10 nejlepších a z nich náhodně ukážeme 3 (aby to nebylo pokaždé stejné)
                top_10 = potential_reads.sort_values(by='Average Rating', ascending=False).head(10)
                random_top = top_10.sample(min(3, len(top_10)))
                st.table(random_top[['Title', 'Author', 'Average Rating']])

            with tab3:
                st.write("Short on time? Try these (under 300 pages):")
                short_books = potential_reads[potential_reads['Number of Pages'] < 300]
                if not short_books.empty:
                    st.table(short_books.sample(min(3, len(short_books)))[['Title', 'Author', 'Number of Pages']])
                else:
                    st.info("No short books found in your TBR.")
        else:
            st.warning("Whoops! It looks like you've filtered out everything. Time to add more books to Goodreads?")

    except Exception as e:
        st.error(f"Error processing data: {e}")
