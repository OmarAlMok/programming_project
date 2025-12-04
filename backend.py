from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import json
import os
import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = 'data.db'


def load_books():
    """
    Load the list of books from the JSON data file.
    Returns an empty list if no data file exists.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []


def save_books(books):
    """
    Save the list of books to the JSON data file with indentation for readability.
    """
    with open(DATA_FILE, 'w') as f:
        json.dump(books, f, indent=4)


def filter_books(books, borrowed_filter=None, category=None, name=None):
    """
    Filter books list based on borrowed status, category, and name.
    :param books: list of book dicts
    :param borrowed_filter: 'available' or 'borrowed' or None
    :param category: category string (case-insensitive) or None
    :param name: exact book name string (case-insensitive) or None
    :return: filtered list of books
    """
    if borrowed_filter == 'available':
        books = [b for b in books if not b.get('borrowed', False)]
    elif borrowed_filter == 'borrowed':
        books = [b for b in books if b.get('borrowed', False)]
    if category:
        books = [b for b in books if b.get('category', '').lower() == category.lower()]
    if name:
        books = [b for b in books if b.get('name', '').lower() == name.lower()]
    return books


@app.route('/books', methods=['GET'])
def get_books():
    """
    Get all books with optional filters for borrowed status, category, and name.
    Adds an 'id' field to each book based on its index.
    """
    books = load_books()
    borrowed_filter = request.args.get('borrowed')
    category = request.args.get('category')
    name = request.args.get('name')
    filtered = filter_books(books, borrowed_filter, category, name)

    # Add id based on position index
    for i, book in enumerate(filtered):
        book['id'] = i

    return jsonify(filtered)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get details of a single book by its ID (index).
    Returns 404 if book not found.
    """
    books = load_books()
    if 0 <= book_id < len(books):
        return jsonify(books[book_id])
    return jsonify({'error': 'Book not found'}), 404


@app.route('/books', methods=['POST'])
def create_book():
    """
    Add a new book. Expects JSON or form data with
    fields: name, publication_date, author, category.
    """
    books = load_books()
    data = request.get_json() if request.is_json else request.form.to_dict()
    required_fields = ('name', 'publication_date', 'author', 'category')

    # Check for missing fields
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    data['borrowed'] = False
    books.append(data)
    save_books(books)
    if request.is_json:
        return jsonify(data), 201
    else:
        # Redirect to main page for form submissions
        return redirect('/')


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book by its ID.
    """
    books = load_books()
    if 0 <= book_id < len(books):
        deleted = books.pop(book_id)
        save_books(books)
        return jsonify(deleted)
    return jsonify({'error': 'Book not found'}), 404


def update_borrowed_status(book_id, borrowed_status):
    """
    Helper function to update borrowed status of a book.
    Returns tuple (success: bool, response: dict or tuple with error and code).
    """
    books = load_books()
    if 0 <= book_id < len(books):
        if books[book_id].get('borrowed', False) == borrowed_status:
            err_msg = 'Book already borrowed' if borrowed_status else 'Book not borrowed'
            return False, (jsonify({'error': err_msg}), 400)
        books[book_id]['borrowed'] = borrowed_status
        save_books(books)
        return True, jsonify(books[book_id])
    return False, (jsonify({'error': 'Book not found'}), 404)


@app.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    """
    Mark a book as borrowed. Expects optional JSON or form data with 'due_date' (dd.mm.yyyy).
    Sets borrow_date automatically to current date.
    """
    books = load_books()
    if not (0 <= book_id < len(books)):
        return jsonify({'error': 'Book not found'}), 404
    if books[book_id].get('borrowed', False):
        return jsonify({'error': 'Book already borrowed'}), 400
    books[book_id]['borrowed'] = True
    books[book_id]['borrow_date'] = datetime.datetime.now().strftime('%d.%m.%Y')
    data = request.get_json() if request.is_json else request.form.to_dict()
    if data and 'due_date' in data:
        books[book_id]['due_date'] = data['due_date']
    save_books(books)
    return jsonify(books[book_id])


@app.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    """
    Mark a book as returned (not borrowed).
    Clears borrow_date and due_date.
    """
    books = load_books()
    if not (0 <= book_id < len(books)):
        return jsonify({'error': 'Book not found'}), 404
    if not books[book_id].get('borrowed', False):
        return jsonify({'error': 'Book not borrowed'}), 400
    books[book_id]['borrowed'] = False
    if 'borrow_date' in books[book_id]:
        del books[book_id]['borrow_date']
    if 'due_date' in books[book_id]:
        del books[book_id]['due_date']
    save_books(books)
    return jsonify(books[book_id])


@app.route('/web/borrow/<int:book_id>', methods=['POST'])
def web_borrow_book(book_id):
    """
    Web interface: borrow a book and redirect to main page.
    """
    borrow_book(book_id)
    return redirect('/')


@app.route('/web/return/<int:book_id>', methods=['POST'])
def web_return_book(book_id):
    """
    Web interface: return a book and redirect to main page.
    """
    return_book(book_id)
    return redirect('/')


@app.route('/web/delete/<int:book_id>', methods=['POST'])
def web_delete_book(book_id):
    """
    Web interface: delete a book and redirect to main page.
    """
    books = load_books()
    if 0 <= book_id < len(books):
        books.pop(book_id)
        save_books(books)
    return redirect('/')


def render_book_row(book, idx):
    """
    Helper function to generate a table row HTML string for one book in the web UI.
    Marks row red if borrowed and due_date is past today.
    """
    status = "Borrowed" if book.get('borrowed', False) else "Available"
    actions = ""
    if not book.get('borrowed', False):
        actions += f'<form method="post" action="/web/borrow/{idx}" style="display:inline;"><input type="text" name="due_date" placeholder="dd.mm.yyyy" required><button type="submit">Borrow</button></form>'
    else:
        actions += f'<form method="post" action="/web/return/{idx}" style="display:inline;"><button type="submit">Return</button></form>'
    actions += f'<form method="post" action="/web/delete/{idx}" style="display:inline;"><button type="submit">Delete</button></form>'
    actions += f'<form method="get" action="/edit/{idx}" style="display:inline; margin-left: 5px;"><button type="submit">Edit</button></form>'

    # Check if overdue
    today = datetime.datetime.now().strftime('%d.%m.%Y')
    due_date = book.get('due_date', '')
    is_overdue = book.get('borrowed', False) and due_date and due_date < today
    row_style = 'style="background-color: red;"' if is_overdue else ''

    return f"""
    <tr {row_style}>
        <td>{book.get('name','')}</td>
        <td>{book.get('author','')}</td>
        <td>{book.get('publication_date','')}</td>
        <td>{book.get('category','')}</td>
        <td>{status}</td>
        <td>{book.get('borrow_date','')}</td>
        <td>{book.get('due_date','')}</td>
        <td>{actions}</td>
    </tr>
    """


@app.route('/')
def index():
    """
    Web UI main page that displays the list of books with filters.
    Filters supported: borrowed status, name search, category.
    """
    books = load_books()
    borrowed_filter = request.args.get('borrowed')
    name_search = request.args.get('name')
    category_filter = request.args.get('category')

    filtered_books = []
    for idx, book in enumerate(books):
        if borrowed_filter == 'available' and book.get('borrowed', False):
            continue
        elif borrowed_filter == 'borrowed' and not book.get('borrowed', False):
            continue
        if name_search and book.get('name', '').lower() != name_search.lower():
            continue
        if category_filter and book.get('category', '').lower() != category_filter.lower():
            continue
        filtered_books.append((idx, book))

    table_rows = "".join([render_book_row(book, idx) for idx, book in filtered_books])

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Online Library</title>
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            form {{ margin: 0; display: inline; }}
            body {{ background-color: #ADD8E6; }}
        </style>
    </head>
    <body>
        <h1>Online Library</h1>
        <form method="get" style="margin-bottom: 10px;">
            <select name="borrowed">
                <option value="" {"selected" if not borrowed_filter else ""}>All</option>
                <option value="available" {"selected" if borrowed_filter=="available" else ""}>Available</option>
                <option value="borrowed" {"selected" if borrowed_filter=="borrowed" else ""}>Borrowed</option>
            </select>
            <select name="category" style="margin-left: 10px;">
                <option value="" {"selected" if not category_filter else ""}>All Categories</option>
                <option value="Fiction" {"selected" if category_filter=="Fiction" else ""}>Fiction</option>
                <option value="Non-Fiction" {"selected" if category_filter=="Non-Fiction" else ""}>Non-Fiction</option>
                <option value="Science" {"selected" if category_filter=="Science" else ""}>Science</option>
                <option value="History" {"selected" if category_filter=="History" else ""}>History</option>
                <option value="Philosophy" {"selected" if category_filter=="Philosophy" else ""}>Philosophy</option>
            </select>
            <button type="submit">Filter</button>
        </form>
        <form method="get" style="margin-bottom: 10px;">
            <input name="name" placeholder="Search by exact name" value="{name_search or ''}">
            <button type="submit">Search</button>
        </form>
        <form method="post" action="/books" style="margin-bottom: 10px;">
            <input name="name" placeholder="Name" required>
            <input name="publication_date" placeholder="Publication Date" required>
            <input name="author" placeholder="Author" required>
            <select name="category" required>
                <option value="" disabled selected>Select Category</option>
                <option value="Fiction">Fiction</option>
                <option value="Non-Fiction">Non-Fiction</option>
                <option value="Science">Science</option>
                <option value="History">History</option>
                <option value="Philosophy">Philosophy</option>
            </select>
            <button type="submit">Add Book</button>
        </form>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Author</th>
                    <th>Publication Date</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Borrow Date</th>
                    <th>Due Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """


@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    """
    Edit a book's details via web form.
    Supports GET to show form and POST to submit updates.
    """
    books = load_books()
    if book_id < 0 or book_id >= len(books):
        return "Book not found", 404

    if request.method == 'POST':
        form = request.form
        # Validate required fields
        required_fields = ('name', 'publication_date', 'author', 'category')
        if not all(k in form for k in required_fields):
            return "Missing fields", 400

        # Update book info
        books[book_id]['name'] = form['name']
        books[book_id]['publication_date'] = form['publication_date']
        books[book_id]['author'] = form['author']
        books[book_id]['category'] = form['category']
        save_books(books)
        return redirect('/')

    # Show edit form
    book = books[book_id]
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Edit Book</title>
        <style>
            body {{ background-color: #ADD8E6; }}
        </style>
    </head>
    <body>
        <h1>Edit Book</h1>
        <form method="post" action="/edit/{book_id}">
            <label for="name">Name:</label><br />
            <input type="text" id="name" name="name" value="{book.get('name', '')}" required /><br /><br />
            <label for="publication_date">Publication Date:</label><br />
            <input type="text" id="publication_date" name="publication_date" value="{book.get('publication_date', '')}" required /><br /><br />
            <label for="author">Author:</label><br />
            <input type="text" id="author" name="author" value="{book.get('author', '')}" required /><br /><br />
            <label for="category">Category:</label><br />
            <select id="category" name="category" required>
                <option value="Fiction" {"selected" if book.get('category') == "Fiction" else ""}>Fiction</option>
                <option value="Non-Fiction" {"selected" if book.get('category') == "Non-Fiction" else ""}>Non-Fiction</option>
                <option value="Science" {"selected" if book.get('category') == "Science" else ""}>Science</option>
                <option value="History" {"selected" if book.get('category') == "History" else ""}>History</option>
                <option value="Philosophy" {"selected" if book.get('category') == "Philosophy" else ""}>Philosophy</option>
            </select><br /><br />
            <button type="submit">Update Book</button>
        </form>
        <p><a href="/">Back to Library</a></p>
    </body>
    </html>
    """
