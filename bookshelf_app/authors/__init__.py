from flask import Blueprint

authors_bp = Blueprint('authors', __name__)


from bookshelf_app.authors import authors
