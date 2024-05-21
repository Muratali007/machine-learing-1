from flask import Flask
from .data_loader import DataLoader

def create_app():
    app = Flask(__name__)

    book_map_path = 'ml_data/book_id_map.csv'
    interactions_path = 'ml_data/goodreads_interactions.csv'
    book_titles_path = 'ml_data/books_titles.json'

    data_loader = DataLoader(book_map_path, interactions_path, book_titles_path)
    app.config['DATA_LOADER'] = data_loader

    from .controllers import main
    app.register_blueprint(main)

    return app
