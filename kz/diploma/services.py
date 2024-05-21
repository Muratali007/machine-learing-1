# app/services.py
import pandas as pd
import logging as log
def generate_recommendations(liked_books, data_loader):
    csv_book_mapping = data_loader.csv_book_mapping
    interactions = data_loader.interactions
    books_titles = data_loader.books_titles

    overlap_users = set()
    for interaction in interactions:
        user_id, csv_id, _, rating, _ = interaction
        try:
            rating = int(rating)
        except ValueError:
            continue
        book_id = csv_book_mapping.get(csv_id)
        if not book_id:
            continue
        if book_id in liked_books and rating >= 4:
            overlap_users.add(user_id)

    log.info(f'Overlap users: {len(overlap_users)}')

    rec_lines = []
    for interaction in interactions:
        user_id, csv_id, _, rating, _ = interaction
        if user_id in overlap_users:
            book_id = csv_book_mapping.get(csv_id)
            if not book_id:
                continue
            rec_lines.append([user_id, book_id, rating])

    log.info(rf'Recommendations: {len(rec_lines)}')

    recs = pd.DataFrame(rec_lines, columns=["user_id", "book_id", "rating"])
    recs["book_id"] = recs["book_id"].astype(str)

    top_recs = recs["book_id"].value_counts().head(10).index.values

    books_titles["book_id"] = books_titles["book_id"].astype(str)

    popular_books = books_titles[books_titles["book_id"].isin(top_recs)]

    all_recs = recs["book_id"].value_counts().to_frame().reset_index()
    all_recs.columns = ["book_id", "book_count"]

    all_recs = all_recs.merge(books_titles, how="inner", on="book_id")

    all_recs["score"] = all_recs["book_count"] * (all_recs["book_count"] / all_recs["ratings"])

    all_recs.sort_values("score", ascending=False, inplace=True)

    popular_recs = all_recs[all_recs["book_count"] > 75].sort_values("score", ascending=False)

    log.info("Popular books: %s", popular_books)
    log.info("Popular books second: %s", popular_recs[~popular_recs["book_id"].isin(liked_books)].head(10))

    return popular_recs[~popular_recs["book_id"].isin(liked_books)].head(10)

def make_clickable(val):
    return f'<a target="_blank" href="{val}">BookHub</a>'

def show_image(val):
    return f'<img src="{val}" width=50></img>'
