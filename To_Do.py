from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'data.db'

def load_books():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_books(books):
    with open(DATA_FILE, 'w') as f:
        json.dump(books, f, indent=4)

@app.route('/books', methods=['GET'])
def get_books():
    books = load_books()
    for i, book in enumerate(books):
        book['id'] = i
    borrowed_filter = request.args.get('borrowed')
    category = request.args.get('category')
    name = request.args.get('name')
    if borrowed_filter == 'available':
        books = [b for b in books if not b['borrowed']]
    elif borrowed_filter == 'borrowed':
        books = [b for b in books if b['borrowed']]
    if category:
        books = [b for b in books if b['category'].lower() == category.lower()]
    if name:
        books = [b for b in books if b['name'].lower() == name.lower()]
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    books = load_books()
    if 0 <= book_id < len(books):
        return jsonify(books[book_id])
    return jsonify({'error': 'Book not found'}), 404

@app.route('/books', methods=['POST'])
def create_book():
    books = load_books()
    data = request.get_json() if request.is_json else request.form.to_dict()
    if not all(k in data for k in ('name', 'publication_date', 'author', 'category')):
        return jsonify({'error': 'Missing fields'}), 400
    data['borrowed'] = False
    books.append(data)
    save_books(books)
    if request.is_json:
        return jsonify(data), 201
    else:
        return redirect('/')

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    books = load_books()
    if 0 <= book_id < len(books):
        deleted = books.pop(book_id)
        save_books(books)
        return jsonify(deleted)
    return jsonify({'error': 'Book not found'}), 404

@app.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    books = load_books()
    if 0 <= book_id < len(books):
        if books[book_id]['borrowed']:
            return jsonify({'error': 'Book already borrowed'}), 400
        books[book_id]['borrowed'] = True
        save_books(books)
        return jsonify(books[book_id])
    return jsonify({'error': 'Book not found'}), 404

@app.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    books = load_books()
    if 0 <= book_id < len(books):
        if not books[book_id]['borrowed']:
            return jsonify({'error': 'Book not borrowed'}), 400
        books[book_id]['borrowed'] = False
        save_books(books)
        return jsonify(books[book_id])
    return jsonify({'error': 'Book not found'}), 404

@app.route('/web/borrow/<int:book_id>', methods=['POST'])
def web_borrow_book(book_id):
    borrow_book(book_id)
    return redirect('/')

@app.route('/web/return/<int:book_id>', methods=['POST'])
def web_return_book(book_id):
    return_book(book_id)
    return redirect('/')

@app.route('/web/delete/<int:book_id>', methods=['POST'])
def web_delete_book(book_id):
    books = load_books()
    if 0 <= book_id < len(books):
        books.pop(book_id)
        save_books(books)
    return redirect('/')

@app.route('/')
def index():
    books = load_books()
    borrowed_filter = request.args.get('borrowed')
    name_search = request.args.get('name')
    filtered_books = []
    for idx, book in enumerate(books):
        if borrowed_filter == 'available' and book['borrowed']:
            continue
        elif borrowed_filter == 'borrowed' and not book['borrowed']:
            continue
        if name_search and book['name'].lower() != name_search.lower():
            continue
        filtered_books.append((idx, book))
    table_rows = ""
    for idx, book in filtered_books:
        status = "Borrowed" if book['borrowed'] else "Available"
        actions = ""
        if not book['borrowed']:
            actions += f'<form method="post" action="/web/borrow/{idx}" style="display:inline;"><button type="submit">Borrow</button></form>'
        else:
            actions += f'<form method="post" action="/web/return/{idx}" style="display:inline;"><button type="submit">Return</button></form>'
        actions += f'<form method="post" action="/web/delete/{idx}" style="display:inline;"><button type="submit">Delete</button></form>'
        table_rows += f"""
        <tr>
            <td>{book['name']}</td>
            <td>{book['author']}</td>
            <td>{book['publication_date']}</td>
            <td>{book['category']}</td>
            <td>{status}</td>
            <td>{actions}</td>
        </tr>
        """
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
            form {{ margin: 0; }}
        </style>
    </head>
    <body>
        <h1>Online Library</h1>
        <form method="get" style="margin-bottom: 10px;">
            <select name="borrowed">
                <option value="">All</option>
                <option value="available">Available</option>
                <option value="borrowed">Borrowed</option>
            </select>
            <button type="submit">Filter</button>
        </form>
        <form method="get" style="margin-bottom: 10px;">
            <input name="name" placeholder="Search by exact name">
            <button type="submit">Search</button>
        </form>
        <form method="post" action="/books" style="margin-bottom: 10px;">
            <input name="name" placeholder="Name" required>
            <input name="publication_date" placeholder="Publication Date" required>
            <input name="author" placeholder="Author" required>
            <input name="category" placeholder="Category" required>
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

if __name__ == '__main__':
    import multiprocessing
    def run_app():
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    process = multiprocessing.Process(target=run_app)
    process.start()
    print("Flask server started in background on http://localhost:5000")
    print("You can now run the GUI in another terminal: py too.py")
    input("Press Enter to stop the server...")
    process.terminate()
