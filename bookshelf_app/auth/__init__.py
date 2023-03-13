from flask import Blueprint

auth_bp = Blueprint('auth', __name__)


from bookshelf_app.auth import auth
