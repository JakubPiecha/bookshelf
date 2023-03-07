import json
from pathlib import Path
from datetime import datetime

from sqlalchemy import text

from bookshelf_app import app, db
from bookshelf_app.models import Author


@app.cli.group()
def db_manage():
    '''Database managment commands'''
    pass
@db_manage.command()
def add_data():
    '''Add data to database'''
    try:
        authors_path = Path(__file__).parent / 'samples' / 'authors.json'
        with open(authors_path) as file:
            data_json = json.load(file)

        for item in data_json:
            item['birth_date'] = datetime.strptime(item['birth_date'], '%d-%m-%Y').date()
            author = Author(**item)
            db.session.add(author)
        db.session.commit()
        print('Data has been add to database')
    except Exception as exc:
        print(' Unexpected error: {}'.format(exc))


@db_manage.command()
def remove_data():
    '''Remove data from database'''
    try:
        db.session.execute(text('TRUNCATE TABLE authors'))
        db.session.commit()
        print('Data has been remove from database')
    except Exception as exc:
        print(' Unexpected error: {}'.format(exc))
