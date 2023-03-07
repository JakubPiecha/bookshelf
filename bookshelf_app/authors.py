from flask import jsonify
from bookshelf_app import app
from


@app.route('/api/v1/authors', methods=["GET"])
def get_authors():
    return jsonify({
        'success': True,
        'data': 'Get all authors'
    })


@app.route('/api/v1/authors/<int:author_id>', methods=["GET"])
def get_author(author_id):
    return jsonify({
        'success': True,
        'data': f'Get author id {author_id}'
    })


@app.route('/api/v1/authors', methods=["POST"])
def create_author():
    return jsonify({
        'success': True,
        'data': 'Create new author'
    }), 201


@app.route('/api/v1/authors/<int:author_id>', methods=["PUT"])
def update_author(author_id):
    return jsonify({
        'success': True,
        'data': f'Change author id {author_id}'
    })


@app.route('/api/v1/authors/<int:author_id>', methods=["DELETE"])
def delete_author(author_id):
    return jsonify({
        'success': True,
        'data': f'Author id {author_id} has been deleted'
    })
