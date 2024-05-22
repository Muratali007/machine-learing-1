# diploma/data_loader.py
import pandas as pd
import logging as log
import gzip

class DataLoader:
    def __init__(self, book_map_path, interactions_path, book_titles_path):
        self.book_map_path = book_map_path
        self.interactions_path = interactions_path
        self.book_titles_path = book_titles_path
        self.csv_book_mapping = {}
        self.interactions = pd.DataFrame()
        self.books_titles = pd.DataFrame()
        self.load_data()

    def load_data(self):
        self.csv_book_mapping = self.read_csv_to_dict(self.book_map_path)
        self.interactions = self.read_interactions(self.interactions_path)
        self.books_titles = pd.read_json(self.book_titles_path)

    def read_csv_to_dict(self, file_path):
        log.info("Reading CSV to dict")
        return pd.read_csv(file_path).set_index('csv_id')['book_id'].to_dict()

    def read_interactions(self, file_path):
        log.info("Reading interactions")
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt') as f:
                return pd.read_csv(f)
        else:
            return pd.read_csv(file_path)
