import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from bookshelf_app import db
from bookshelf_app.commands import db_manage_bp
from bookshelf_app.models import Author, Book


def load_json_data(file_name):
    data_path = Path(__file__).parent.parent / 'samples' / file_name
    with open(data_path) as file:
        data_json = json.load(file)
    return data_json



@db_manage_bp.cli.group()
def db_manage():
    '''Database managment commands'''
    pass
@db_manage.command()
def add_data():
    '''Add data to database'''
    try:
        data_json = load_json_data('authors.json')
        for item in data_json:
            item['birth_date'] = datetime.strptime(item['birth_date'], '%d-%m-%Y').date()
            author = Author(**item)
            db.session.add(author)
        data_json = load_json_data('books.json')
        for item in data_json:
            book = Book(**item)
            db.session.add(book)
        db.session.commit()
        print('Data has been add to database')
    except Exception as exc:
        print(' Unexpected error: {}'.format(exc))


@db_manage.command()
def remove_data():
    '''Remove data from database'''
    try:

        db.session.execute(text('DELETE FROM books'))
        db.session.execute(text('ALTER TABLE books AUTO_INCREMENT = 1'))
        db.session.execute(text('DELETE FROM authors'))
        db.session.execute(text('ALTER TABLE authors AUTO_INCREMENT = 1'))
        db.session.commit()
        print('Data has been remove from database')
    except Exception as exc:
        print(' Unexpected error: {}'.format(exc))
