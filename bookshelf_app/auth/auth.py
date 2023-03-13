from flask import abort, jsonify
from webargs.flaskparser import use_args

from bookshelf_app import db
from bookshelf_app.auth import auth_bp
from bookshelf_app.models import user_schema, User, UserSchema, user_pasword_change_chema
from bookshelf_app.utils import validate_json_content_type, token_required


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

@auth_bp.route('/user', methods=['GET'])
@token_required
def get_current_user(user_id):
    user = User.query.get_or_404(user_id, description=f'User {user_id} not found')

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })

@auth_bp.route('/change/password', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(user_pasword_change_chema, error_status_code=400)
def change_user_password(user_id, args):
    user = User.query.get_or_404(user_id, description=f'User {user_id} not found')
    if not user.valid_password(args['current_password']):
        abort(401, description='Wrong password')

    user.password = user.generate_hashed_password(args['new_password'])
    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })

@auth_bp.route('/change/data', methods=['PUT'])
@token_required
@validate_json_content_type
@use_args(UserSchema(only=['username', 'email']), error_status_code=400)
def change_user_data(user_id, args):
    user = User.query.get_or_404(user_id, description=f'User {user_id} not found')
    if user.username != args['username']:
        if User.query.filter(User.username == args['username']).first():
            abort(409, description=f'User with username {args["username"]} already exists')
    if user.email != args['email']:
        if User.query.filter(User.email == args['email']).first():
            abort(409, description=f'User with email {args["email"]} already exists')


    user.username = args['username']
    user.email = args['email']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })