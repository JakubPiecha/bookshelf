import re
from functools import wraps

from flask import request, url_for, current_app
from flask_sqlalchemy import DefaultMeta
from flask_sqlalchemy.query import Query
from werkzeug.exceptions import UnsupportedMediaType

from config import Config

COMPARISON_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')


def validate_json_content_type(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json(silent=True)
        if data is None:
            raise UnsupportedMediaType('Content type must be application/json')
        return func(*args, **kwargs)

    return wrapper


def get_schema_args(model: DefaultMeta) -> dict:
    schema_args = {'many': True}
    fields = request.args.get('fields')
    if fields:
        schema_args['only'] = [field for field in fields.split(',') if field in model.__table__.columns]
    return schema_args


def apply_order(model: DefaultMeta, query: Query) -> Query:
    sort_fields = request.args.get('sort')
    if sort_fields:
        for field in sort_fields.split(','):
            desc = False
            if field.startswith('-'):
                field = field[1:]
                desc = True
            column_attr = getattr(model, field, None)
            if column_attr is not None:
                query = query.order_by(column_attr.desc()) if desc else query.order_by(column_attr)
    return query


def _get_filter_argument(column_name, value, operator):
    operator_maping = {
        '==': column_name == value,
        'gte': column_name >= value,
        'gt': column_name > value,
        'lte': column_name <= value,
        'lt': column_name < value,
    }
    return operator_maping[operator]


def apply_filter(model, query: Query):
    for param, value in request.args.items():
        if param not in {'fields', 'sort', 'page', 'limit'}:
            operator = '=='
            match = COMPARISON_OPERATORS_RE.match(param)
            if match is not None:
                param, operator = match.groups()
            column_attr = getattr(model, param, None)
            if column_attr is not None:
                value = model.additional_validation(param, value)
                # if value is None:
                #     continue
                filter_argument = _get_filter_argument(column_attr, value, operator)
                query = query.filter(filter_argument)
    return query


def get_pagination(query, func_name):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', current_app.config.get('PER_PAGE', 5), type=int)
    paginate_obj = query.paginate(page=page, per_page=limit, error_out=False)
    params = {key: value for key, value in request.args.items() if key != 'page'}
    pagination = {
        'total_pages': paginate_obj.pages,
        'total_records': paginate_obj.total,
        'current_page': url_for(func_name, page=page, **params),
    }
    if paginate_obj.has_next:
        pagination['next_page'] = url_for(func_name, page=page + 1, **params)

    if paginate_obj.has_prev:
        pagination['prev_page'] = url_for(func_name, page=page - 1, **params)
    return paginate_obj.items, pagination
