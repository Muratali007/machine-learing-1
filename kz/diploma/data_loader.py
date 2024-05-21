import pandas as pd
import logging as log
from .utils import read_csv_to_dict, read_json

class DataLoader:
    def __init__(self, book_map_path, interactions_path, book_titles_path):
        self.book_map_path = book_map_path
        self.interactions_path = interactions_path
        self.book_titles_path = book_titles_path
        self.csv_book_mapping = {}
        self.interactions = []
        self.books_titles = pd.DataFrame()
        self.load_data()

    def load_data(self):
        self.csv_book_mapping = read_csv_to_dict(self.book_map_path)
        self.interactions = self.read_interactions(self.interactions_path)
        self.books_titles = read_json(self.book_titles_path)

    def read_interactions(self, file_path):
        log.info('start log')
        interactions = []
        with open(file_path, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                interactions.append(line.strip().split(","))
        return interactions
