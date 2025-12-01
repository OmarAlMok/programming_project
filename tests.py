import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QTableWidgetItem
from PyQt6.QtCore import Qt

# Add the current directory to sys.path to import gui module
sys.path.insert(0, os.path.dirname(__file__))

from gui import AddBookDialog, BorrowBookDialog, MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Fixture to create a QApplication instance for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_add_book_dialog_initialization(qapp):
    """Test AddBookDialog initialization."""
    dialog = AddBookDialog()
    assert dialog.windowTitle() == "Add New Book"
    assert isinstance(dialog.name_edit, QLineEdit)
    assert isinstance(dialog.date_edit, QLineEdit)
    assert isinstance(dialog.author_edit, QLineEdit)
    assert isinstance(dialog.category_edit, QLineEdit)
    assert isinstance(dialog.ok_btn, QPushButton)
    dialog.close()


def test_add_book_dialog_accept(qapp):
    """Test AddBookDialog accept behavior."""
    dialog = AddBookDialog()
    dialog.name_edit.setText("Test Book")
    dialog.date_edit.setText("01.01.2023")
    dialog.author_edit.setText("Test Author")
    dialog.category_edit.setText("Fiction")
    dialog.ok_btn.click()
    assert dialog.result() == 1  # QDialog.Accepted
    dialog.close()


def test_borrow_book_dialog_initialization(qapp):
    """Test BorrowBookDialog initialization."""
    dialog = BorrowBookDialog()
    assert dialog.windowTitle() == "Borrow Book"
    assert isinstance(dialog.due_date_edit, QLineEdit)
    assert dialog.due_date_edit.placeholderText() == "dd.mm.yyyy"
    assert isinstance(dialog.ok_btn, QPushButton)
    dialog.close()


def test_borrow_book_dialog_accept(qapp):
    """Test BorrowBookDialog accept behavior."""
    dialog = BorrowBookDialog()
    dialog.due_date_edit.setText("15.12.2023")
    dialog.ok_btn.click()
    assert dialog.result() == 1  # QDialog.Accepted
    dialog.close()


def test_main_window_populate_table(qapp):
    """Test MainWindow populate_table method."""
    window = MainWindow()
    books = [
        {"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False},
        {"name": "Book2", "author": "Author2", "publication_date": "01.01.2021", "category": "Non-Fiction", "borrowed": True, "due_date": "01.01.2024"}
    ]
    window.populate_table(books)
    assert window.table_widget.rowCount() == 2
    assert window.table_widget.item(0, 0).text() == "Book1"
    assert window.table_widget.item(1, 0).text() == "Book2"
    assert window.table_widget.item(1, 4).text() == "Borrowed"
    window.close()


@patch('requests.get')
def test_main_window_load_books(mock_get, qapp):
    """Test MainWindow load_books method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False}
    ]
    mock_get.return_value = mock_response

    window = MainWindow()
    window.load_books()
    assert window.table_widget.rowCount() == 1
    assert window.table_widget.item(0, 0).text() == "Book1"
    window.close()


@patch('requests.get')
def test_main_window_search(mock_get, qapp):
    """Test MainWindow search method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False}
    ]
    mock_get.return_value = mock_response

    window = MainWindow()
    window.search_edit.setText("Book1")
    window.search()
    mock_get.assert_called_with("http://localhost:5000/books", params={'name': 'Book1'})
    assert window.table_widget.rowCount() == 1
    assert window.table_widget.item(0, 0).text() == "Book1"
    window.close()


@patch('requests.get')
def test_main_window_filter_books(mock_get, qapp):
    """Test MainWindow filter_books method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False}
    ]
    mock_get.return_value = mock_response

    window = MainWindow()
    window.category_combo.setCurrentText("Fiction")
    window.filter_books()
    mock_get.assert_called_with("http://localhost:5000/books", params={'category': 'Fiction'})
    assert window.table_widget.rowCount() == 1
    assert window.table_widget.item(0, 0).text() == "Book1"
    window.close()


@patch('requests.post')
@patch('gui.QMessageBox.warning')
def test_main_window_add_book(mock_warning, mock_post, qapp):
    """Test MainWindow add_book method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response

    window = MainWindow()
    dialog = AddBookDialog()
    dialog.name_edit.setText("New Book")
    dialog.date_edit.setText("01.01.2023")
    dialog.author_edit.setText("New Author")
    dialog.category_edit.setText("Fiction")
    window.add_btn.clicked.connect(lambda: window.add_book())
    # Simulate dialog exec
    with patch.object(dialog, 'exec', return_value=1):
        window.add_book()
    mock_post.assert_called_with("http://localhost:5000/books", json={
        'name': 'New Book',
        'publication_date': '01.01.2023',
        'author': 'New Author',
        'category': 'Fiction'
    })
    window.close()


@patch('requests.delete')
@patch('gui.QMessageBox.warning')
def test_main_window_delete_book(mock_warning, mock_delete, qapp):
    """Test MainWindow delete_book method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_delete.return_value = mock_response

    window = MainWindow()
    # Set up table with a book
    books = [{"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False}]
    window.populate_table(books)
    window.table_widget.setCurrentRow(0)
    window.delete_book()
    mock_delete.assert_called_with("http://localhost:5000/books/0")
    window.close()


@patch('requests.post')
@patch('gui.QMessageBox.warning')
def test_main_window_borrow_book(mock_warning, mock_post, qapp):
    """Test MainWindow borrow_book method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    window = MainWindow()
    # Set up table with a book
    books = [{"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False}]
    window.populate_table(books)
    window.table_widget.setCurrentRow(0)
    dialog = BorrowBookDialog()
    dialog.due_date_edit.setText("15.12.2023")
    with patch.object(dialog, 'exec', return_value=1):
        window.borrow_book()
    mock_post.assert_called_with("http://localhost:5000/books/0/borrow", json={'due_date': '15.12.2023'})
    window.close()


@patch('requests.post')
@patch('gui.QMessageBox.warning')
def test_main_window_return_book(mock_warning, mock_post, qapp):
    """Test MainWindow return_book method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    window = MainWindow()
    # Set up table with a borrowed book
    books = [{"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": True}]
    window.populate_table(books)
    window.table_widget.setCurrentRow(0)
    window.return_book()
    mock_post.assert_called_with("http://localhost:5000/books/0/return")
    window.close()


@patch('requests.get')
@patch('gui.QMessageBox.information')
def test_main_window_show_metadata(mock_info, mock_get, qapp):
    """Test MainWindow show_metadata method with mocked request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False
    }
    mock_get.return_value = mock_response

    window = MainWindow()
    # Set up table with a book
    books = [{"name": "Book1", "author": "Author1", "publication_date": "01.01.2020", "category": "Fiction", "borrowed": False}]
    window.populate_table(books)
    window.table_widget.cellDoubleClicked.emit(0, 0)
    mock_get.assert_called_with("http://localhost:5000/books/0")
    mock_info.assert_called_once()
    window.close()
