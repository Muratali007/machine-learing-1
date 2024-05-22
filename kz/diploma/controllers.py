# diploma/controllers.py
from flask import Blueprint, request, jsonify, current_app
from .services import generate_recommendations, make_clickable, show_image, filter_liked_books
import logging as log

main = Blueprint('main', __name__)


@main.route('/list-of-5', methods=['POST'])
def list_of_5():
    data = request.get_json()
    if not data or 'liked_books' not in data:
        return jsonify({"error": "No input data provided"}), 400

    liked_books = data['liked_books']
    if not isinstance(liked_books, list) or not all(isinstance(book, str) for book in liked_books):
        return jsonify({"error": "Input data should be a list of strings"}), 400

    log.info("start generating recommendations")
    popular_recs = generate_recommendations(liked_books, current_app.config['DATA_LOADER'])

    styled_recs = popular_recs.style.format({'url': make_clickable, 'cover_image': show_image})

    return styled_recs.render(), 200, {'Content-Type': 'text/html'}


@main.route('/filter-liked-books', methods=['POST'])
def filter_liked_books_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    file_path = 'uploaded_file.csv'
    file.save(file_path)

    log.info("start filtering liked books")
    filtered_recs = filter_liked_books(file_path, current_app.config['DATA_LOADER'])

    styled_recs = filtered_recs.style.format({'url': make_clickable, 'cover_image': show_image})

    return styled_recs.render(), 200, {'Content-Type': 'text/html'}
