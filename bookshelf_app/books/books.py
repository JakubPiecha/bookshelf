from flask import jsonify, abort
from webargs.flaskparser import use_args

from bookshelf_app import db
from bookshelf_app.books import books_bp
from bookshelf_app.models import Book, BookSchema, book_schema, Author
from bookshelf_app.utils import get_schema_args, apply_order, apply_filter, get_pagination, validate_json_content_type


@books_bp.route('/books', methods=["GET"])
def get_books():
    query = Book.query
    schema_args = get_schema_args(Book)
    query = apply_order(Book, query)
    query = apply_filter(Book, query)
    items, pagination = get_pagination(query, 'books.get_books')
    books = BookSchema(**schema_args).dump(items)
    return jsonify({
        'success': True,
        'data': books,
        'number of records': len(books),
        'pagination': pagination
    })


@books_bp.route('/books/<int:book_id>', methods=["GET"])
def get_book(book_id):
    book = Book.query.get_or_404(book_id, description=f'Book with id {book_id} not found')
    return jsonify({
        'success': True,
        'data': book_schema.dump(book)
    })


@books_bp.route('/books/<int:book_id>', methods=["PUT"])
@validate_json_content_type
@use_args(book_schema, error_status_code=400)
def update_book(args, book_id):
    book = Book.query.get_or_404(book_id, description=f'Book with id {book_id} not found')
    if book.isbn != args['isbn']:
        if Book.query.filter(Book.isbn == args['isbn']).first():
            abort(409, description=f'Book with ISBN {args["isbn"]} already exists')
    book.title = args['title']
    book.isbn = args['isbn']
    book.number_of_pages = args['number_of_pages']
    description = args.get('description')
    if description is not None:
        book.description = description
    author = args.get('author_id')
    if author is not None:
        Author.query.get_or_404(author, description=f'Author with id {author} not found')
        book.author_id = author
    db.session.commit()
    return jsonify({
        'success': True,
        'data': book_schema.dump(book)
    })


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id, description=f'Book with id {book_id} not found')
    db.session.delete(book)
    db.session.commit()
    return jsonify({
        'success': True,
        'data': f'Book id {book_id} has been deleted'
    })


@books_bp.route('/author/<int:author_id>/books', methods=['GET'])
def all_books_author(author_id):
    Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')
    books = Book.query.filter(Book.author_id == author_id).all()
    return jsonify({
        'success': True,
        'data': BookSchema(many=True, exclude=['author']).dump(books),
        'numbers_of_records': len(books)
    })


@books_bp.route('/author/<int:author_id>/books', methods=['POST'])
@validate_json_content_type
@use_args(BookSchema(exclude=['author_id']), error_status_code=400)
def create_book(args, author_id):
    Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')

    if Book.query.filter(Book.isbn == args['isbn']).first():
        abort(409, description=f'Book with ISBN {args["isbn"]} already exists')

    book = Book(author_id=author_id, **args)

    db.session.add(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': book_schema.dump(book),
    }), 201
