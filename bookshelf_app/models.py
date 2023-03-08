import re
from flask import request, url_for
from flask_sqlalchemy.query import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from typing import Tuple
from datetime import datetime
from marshmallow import Schema, fields, validate, validates, ValidationError
from bookshelf_app import db


from bookshelf_app import Config

COMPARISON_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.first_name} {self.last_name}'

    @staticmethod
    def get_schema_args(fields: str) -> dict:
        schema_args = {'many': True}
        if fields:
            schema_args['only'] = [field for field in fields.split(',') if field in Author.__table__.columns]
        return schema_args

    @staticmethod
    def apply_order(query: Query, sort_fields: str) -> Query:
        if sort_fields:
            for field in sort_fields.split(','):
                desc = False
                if field.startswith('-'):
                    field = field[1:]
                    desc = True
                column_attr = getattr(Author, field, None)
                if column_attr is not None:
                    query = query.order_by(column_attr.desc()) if desc else query.order_by(column_attr)
        return query

    @staticmethod
    def get_filter_argument(column_name: InstrumentedAttribute, value: str, operator: str ) -> BinaryExpression:
        operator_maping = {
            '==': column_name == value,
            'gte': column_name >= value,
            'gt': column_name > value,
            'lte': column_name <= value,
            'lt': column_name < value,
        }
        return operator_maping[operator]

    @staticmethod
    def apply_filter(query: Query) -> Query:
        for param, value in request.args.items():
            if param not in {'fields', 'sort', 'page', 'limit'}:
                operator = '=='
                match = COMPARISON_OPERATORS_RE.match(param)
                if match is not None:
                    param, operator = match.groups()
                column_attr = getattr(Author, param, None)
                if column_attr is not None:
                    if param == 'birth_date':
                        try:
                            value = datetime.strptime(value, '%d-%m-%Y').date()
                        except ValueError:
                            continue
                    filter_argument = Author.get_filter_argument(column_attr, value, operator)
                    query = query.filter(filter_argument)
        return query

    @staticmethod
    def get_pagination(query: Query) -> Tuple[list, dict]:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', Config.PER_PAGE, type=int)
        paginate_obj = query.paginate(page=page, per_page=limit, error_out=False)
        params = {key: value for key, value in request.args.items() if key != 'page'}
        pagination = {
            'total_pages': paginate_obj.pages,
            'total_records': paginate_obj.total,
            'current_page': url_for('authors.get_authors', page=page, **params),
        }
        if paginate_obj.has_next:
            pagination['next_page'] = url_for('authors.get_authors', page=page+1, **params)

        if paginate_obj.has_prev:
            pagination['prev_page'] = url_for('authors.get_authors', page=page-1, **params)
        return paginate_obj.items, pagination

class AuthorSchema(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(max=50))
    last_name = fields.String(required=True, validate=validate.Length(max=50))
    birth_date = fields.Date('%d-%m-%Y', required=True)

    @validates('birth_date')
    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError(f'Birth date must be lower than {datetime.now().date()}')


author_schema = AuthorSchema()
