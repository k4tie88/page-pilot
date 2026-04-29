# --- OPRAVENÁ LOGIKA FILTROVÁNÍ ---

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Seznam poliček, které nechceme
        blacklisted_shelves = [
            'read', 
            'did-not-finish', 
            'author-to-avoid', 
            'not-appealing', 
            'never', 
            'checked-but-not-interested'
        ]

        def is_book_ok(row):
            # 1. Kontrola Exclusive Shelf (vždy přítomno)
            exc_shelf = str(row.get('Exclusive Shelf', '')).lower()
            if exc_shelf in blacklisted_shelves:
                return False
            
            # 2. Kontrola sloupce Bookshelves (ošetření KeyError)
            # Použijeme .get(), aby to nespadlo, když sloupec chybí
            shelves_val = row.get('Bookshelves', '')
            if pd.notna(shelves_val):
                tags = [t.strip().lower() for t in str(shelves_val).split(',')]
                if any(tag in blacklisted_shelves for tag in tags):
                    return False
            
            # 3. Pokud prošla oběma filtry, kniha je OK
            return True

        # Aplikujeme filtr bezpečně
        potential_reads = df[df.apply(is_book_ok, axis=1)].copy()
        
        # Vyfiltrujeme i to, co právě čteš
        potential_reads = potential_reads[potential_reads['Exclusive Shelf'] != 'currently-reading']

        st.write(f"✅ Filtered! Available: {len(potential_reads)} books.")

        # ... zbytek kódu (Taby a doporučení) ...
