from flask import abort, jsonify
from webargs.flaskparser import use_args

from bookshelf_app import db
from bookshelf_app.auth import auth_bp
from bookshelf_app.models import user_schema, User, UserSchema
from bookshelf_app.utils import validate_json_content_type


@auth_bp.route('/register', methods=['POST'])
@validate_json_content_type
@use_args(user_schema, error_status_code=400)
def register(args):
    if User.query.filter(User.username == args['username']).first():
        abort(409, description=f'User with username {args["username"]} already exists')
    if User.query.filter(User.email == args['email']).first():
        abort(409, description=f'User with email {args["email"]} already exists')

    args['password'] = User.generate_hashed_password(args['password'])
    user = User(**args)

    db.session.add(user)
    db.session.commit()

    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    })

@auth_bp.route('/login', methods=['POST'])
@validate_json_content_type
@use_args(UserSchema(only=['username', 'password']), error_status_code=400)
def login(args):
    user = User.query.filter(User.username == args['username']).first()
    if not user:
        abort(401, description=f'Wrong login or password')
    if not user.valid_password(args['password']):
        abort(401, description=f'Wrong login or password')

    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    })