# diploma/services.py
import pandas as pd
import logging as log
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.sparse import coo_matrix


def generate_recommendations(liked_books, data_loader):
    # Use preloaded data
    csv_book_mapping = data_loader.csv_book_mapping
    interactions = data_loader.interactions
    books_titles = data_loader.books_titles

    # Ensure liked_books are mapped correctly
    liked_books_ids = [csv_book_mapping.get(book) for book in liked_books if book in csv_book_mapping]

    overlap_users = interactions[interactions['book_id'].isin(liked_books_ids) & (interactions['rating'] >= 4)][
        'user_id'].unique()

    log.info(f'Overlap users: {len(overlap_users)}')

    rec_lines = interactions[interactions['user_id'].isin(overlap_users)]

    log.info(f'Recommendations: {len(rec_lines)}')

    recs = rec_lines.groupby('book_id').size().reset_index(name='counts').sort_values(by='counts', ascending=False)
    top_recs = recs.head(10)

    popular_books = books_titles[books_titles['book_id'].isin(top_recs['book_id'])]

    log.info("Popular books: %s", popular_books)

    return popular_books


def make_clickable(val):
    return f'<a target="_blank" href="{val}">BookHub</a>'


def show_image(val):
    return f'<img src="{val}" width=50></img>'


def filter_liked_books(file_path, data_loader):
    # Use preloaded data
    file_book_id = data_loader.book_map_path
    file_goodread_int = data_loader.interactions_path
    file_book_titles = data_loader.book_titles_path

    my_books = pd.read_csv(file_path, index_col=0)
    my_books["book_id"] = my_books["book_id"].astype(str)

    csv_book_mapping = data_loader.csv_book_mapping
    book_set = set(my_books["book_id"])

    overlap_users = {}
    with open(file_goodread_int) as f:
        while True:
            line = f.readline()
            if not line:
                break
            user_id, csv_id, _, rating, _ = line.strip().split(",")
            book_id = csv_book_mapping.get(csv_id)
            if book_id in book_set:
                if user_id not in overlap_users:
                    overlap_users[user_id] = 1
                else:
                    overlap_users[user_id] += 1

    filtered_overlap_users = set([k for k in overlap_users if overlap_users[k] > my_books.shape[0] / 20])

    interactions_list = []
    with open(file_goodread_int) as f:
        while True:
            line = f.readline()
            if not line:
                break
            user_id, csv_id, _, rating, _ = line.strip().split(",")
            if user_id in filtered_overlap_users:
                book_id = csv_book_mapping[csv_id]
                interactions_list.append([user_id, book_id, rating])

    interactions = pd.DataFrame(interactions_list, columns=["user_id", "book_id", "rating"])
    interactions = pd.concat([my_books[["user_id", "book_id", "rating"]], interactions])
    interactions["book_id"] = interactions["book_id"].astype(str)
    interactions["user_id"] = interactions["user_id"].astype(str)
    interactions["rating"] = pd.to_numeric(interactions["rating"])
    interactions["user_index"] = interactions["user_id"].astype("category").cat.codes
    interactions["book_index"] = interactions["book_id"].astype("category").cat.codes

    ratings_mat_coo = coo_matrix((interactions["rating"], (interactions["user_index"], interactions["book_index"])))
    ratings_mat = ratings_mat_coo.tocsr()

    my_index = 0
    similarity = cosine_similarity(ratings_mat[my_index, :], ratings_mat).flatten()
    indices = np.argpartition(similarity, -300)[-300:]
    similar_users = interactions[interactions["user_index"].isin(indices)].copy()
    similar_users = similar_users[similar_users["user_id"] != "-1"]

    book_recs = similar_users.groupby("book_id").rating.agg(['count', 'mean'])
    books_titles = data_loader.books_titles

    book_recs = book_recs.merge(books_titles, how="inner", on="book_id")
    book_recs["adjusted_count"] = book_recs["count"] * (book_recs["count"] / book_recs["ratings"])
    book_recs["score"] = book_recs["mean"] * book_recs["adjusted_count"]
    book_recs = book_recs[~book_recs["book_id"].isin(my_books["book_id"])]

    my_books["mod_title"] = my_books["title"].str.replace("[^a-zA-Z0-9 ]", "", regex=True).str.lower()
    my_books["mod_title"] = my_books["mod_title"].str.replace("\s+", " ", regex=True)
    book_recs = book_recs[~book_recs["mod_title"].isin(my_books["mod_title"])]
    book_recs = book_recs[book_recs["count"] > 2]
    book_recs = book_recs[book_recs["mean"] > 2]

    return book_recs.sort_values("score", ascending=False)
