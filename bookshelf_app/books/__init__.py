from flask import Blueprint

books_bp = Blueprint('books', __name__)

from bookshelf_app.books import books

