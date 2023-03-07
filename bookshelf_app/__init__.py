from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from sqlalchemy.sql import text

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# with app.app_context():
#     results = db.session.execute(text('show databases'))
#     for row in results:
#         print(row)

from bookshelf_app import authors, models, db_manage_commands


