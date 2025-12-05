# Import required modules for PyQt GUI and HTTP requests
import sys
import requests
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QComboBox,
    QLabel,
    QFormLayout,
    QDialog,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt


class AddBookDialog(QDialog):
    """
    Dialog window to add a new book.
    Contains form fields for the book's name, publication date, author, and category.
    Provides an 'Add' button that accepts the dialog input.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Book")
        layout = QFormLayout()

        # Text input for book name
        self.name_edit = QLineEdit()
        # Text input for publication date
        self.date_edit = QLineEdit()
        # Text input for author name
        self.author_edit = QLineEdit()
        # Text input for book category
        self.category_edit = QLineEdit()

        # Add input fields to the form layout with labels
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Publication Date:", self.date_edit)
        layout.addRow("Author:", self.author_edit)
        layout.addRow("Category:", self.category_edit)

        # Add button to submit the form and accept the dialog
        self.ok_btn = QPushButton("Add")
        self.ok_btn.clicked.connect(self.accept)
        layout.addRow(self.ok_btn)

        self.setLayout(layout)


class BorrowBookDialog(QDialog):
    """
    Dialog window to borrow a book.
    Contains form fields for the borrower name and due date (dd.mm.yyyy).
    Provides a 'Borrow' button that accepts the dialog input.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Borrow Book")
        layout = QFormLayout()

        # Text input for borrower name
        self.borrower_name_edit = QLineEdit()
        self.borrower_name_edit.setPlaceholderText("Borrower Name")

        # Text input for due date
        self.due_date_edit = QLineEdit()
        self.due_date_edit.setPlaceholderText("dd.mm.yyyy")

        # Add input fields to the form layout with labels
        layout.addRow("Borrower Name:", self.borrower_name_edit)
        layout.addRow("Due Date:", self.due_date_edit)

        # Add button to submit the form and accept the dialog
        self.ok_btn = QPushButton("Borrow")
        self.ok_btn.clicked.connect(self.accept)
        layout.addRow(self.ok_btn)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Library")
        self.base_url = "http://localhost:5000"

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Search and filter layout
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name...")
        self.search_btn = QPushButton("Search")
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        categories = ["Fiction", "Non-Fiction", "Science", "History", "Philosophy"]
        for category in categories:
            self.category_combo.addItem(category)
        self.borrowed_combo = QComboBox()
        self.borrowed_combo.addItem("All")
        self.borrowed_combo.addItem("Available")
        self.borrowed_combo.addItem("Borrowed")
        self.refresh_btn = QPushButton("Refresh")
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(QLabel("Category:"))
        search_layout.addWidget(self.category_combo)
        search_layout.addWidget(QLabel("Status:"))
        search_layout.addWidget(self.borrowed_combo)
        search_layout.addWidget(self.refresh_btn)

        # Table widget for displaying books
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Author", "Publication Date", "Category", "Status", "Borrower's Name"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Buttons panel
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Book")
        self.delete_btn = QPushButton("Delete")
        self.borrow_btn = QPushButton("Borrow")
        self.return_btn = QPushButton("Return")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.borrow_btn)
        btn_layout.addWidget(self.return_btn)

        layout.addLayout(search_layout)
        layout.addWidget(self.table_widget)
        layout.addLayout(btn_layout)

        # Connect signals to slots
        self.search_btn.clicked.connect(self.search)
        self.category_combo.currentTextChanged.connect(self.filter_books)
        self.borrowed_combo.currentTextChanged.connect(self.filter_books)
        self.refresh_btn.clicked.connect(self.load_books)
        self.add_btn.clicked.connect(self.add_book)
        self.delete_btn.clicked.connect(self.delete_book)
        self.borrow_btn.clicked.connect(self.borrow_book)
        self.return_btn.clicked.connect(self.return_book)
        self.table_widget.cellDoubleClicked.connect(self.show_metadata)

        # Load initial book list
        self.load_books()

    def populate_table(self, books):
        """
        Populate the QTableWidget with a list of book dictionaries.
        Clears existing rows and sets new rows for each book.
        Marks row red if borrowed and due_date is past today.
        """
        from datetime import datetime
        self.table_widget.setRowCount(len(books))
        today = datetime.now().strftime('%d.%m.%Y')
        for i, book in enumerate(books):
            self.table_widget.setItem(i, 0, QTableWidgetItem(book.get('name', '')))
            self.table_widget.setItem(i, 1, QTableWidgetItem(book.get('author', '')))
            self.table_widget.setItem(i, 2, QTableWidgetItem(book.get('publication_date', '')))
            self.table_widget.setItem(i, 3, QTableWidgetItem(book.get('category', '')))
            status = "Borrowed" if book.get('borrowed', False) else "Available"
            self.table_widget.setItem(i, 4, QTableWidgetItem(status))
            self.table_widget.setItem(i, 5, QTableWidgetItem(book.get('borrower_name', '')))

            # Check if overdue
            due_date = book.get('due_date', '')
            is_overdue = book.get('borrowed', False) and due_date and due_date < today
            if is_overdue:
                for col in range(6):
                    item = self.table_widget.item(i, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.red)

    def load_books(self):
        """
        Load all books from backend and display in the table.
        """
        try:
            response = requests.get(f"{self.base_url}/books")
            if response.status_code == 200:
                books = response.json()
                self.populate_table(books)
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def search(self):
        """
        Search books by exact name and display results in the table.
        """
        name = self.search_edit.text().strip()
        if name:
            try:
                response = requests.get(f"{self.base_url}/books", params={'name': name})
                if response.status_code == 200:
                    books = response.json()
                    self.populate_table(books)
            except requests.exceptions.RequestException:
                QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def filter_books(self):
        """
        Filter books based on category and borrowed status dropdown selections.
        Fetches filtered books from backend and updates the table.
        """
        category = self.category_combo.currentText()
        borrowed = self.borrowed_combo.currentText()
        params = {}
        if category != "All Categories":
            params['category'] = category
        if borrowed != "All":
            params['borrowed'] = borrowed.lower()
        try:
            response = requests.get(f"{self.base_url}/books", params=params)
            if response.status_code == 200:
                books = response.json()
                self.populate_table(books)
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def add_book(self):
        """
        Show dialog to add a new book.
        On success, reload the book list.
        """
        dialog = AddBookDialog()
        if dialog.exec():
            data = {
                'name': dialog.name_edit.text(),
                'publication_date': dialog.date_edit.text(),
                'author': dialog.author_edit.text(),
                'category': dialog.category_edit.text()
            }
            try:
                response = requests.post(f"{self.base_url}/books", json=data)
                if response.status_code == 201:
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", response.json().get('error', 'Failed to add book'))
            except requests.exceptions.RequestException:
                QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def delete_book(self):
        """
        Delete the selected book from the backend and reload table.
        """
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            book_id = current_row
            try:
                response = requests.delete(f"{self.base_url}/books/{book_id}")
                if response.status_code == 200:
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", response.json().get('error', 'Failed to delete book'))
            except requests.exceptions.RequestException:
                QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def borrow_book(self):
        """
        Show dialog to borrow the selected book with borrower name and due date input.
        On success, reload the book list.
        """
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            book_id = current_row
            dialog = BorrowBookDialog()
            if dialog.exec():
                borrower_name = dialog.borrower_name_edit.text().strip()
                due_date = dialog.due_date_edit.text().strip()
                if borrower_name and due_date:
                    data = {'borrower_name': borrower_name, 'due_date': due_date}
                    try:
                        response = requests.post(f"{self.base_url}/books/{book_id}/borrow", json=data)
                        if response.status_code == 200:
                            self.load_books()
                        else:
                            QMessageBox.warning(self, "Error", response.json().get('error', 'Failed to borrow book'))
                    except requests.exceptions.RequestException:
                        QMessageBox.warning(self, "Error", "Cannot connect to backend.")
                else:
                    QMessageBox.warning(self, "Error", "Borrower name and due date are required.")

    def return_book(self):
        """
        Return the selected book via backend and reload table.
        """
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            book_id = current_row
            try:
                response = requests.post(f"{self.base_url}/books/{book_id}/return")
                if response.status_code == 200:
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", response.json().get('error', 'Failed to return book'))
            except requests.exceptions.RequestException:
                QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def show_metadata(self, row, column):
        """
        Show a message box displaying details of the double-clicked book row.
        """
        book_id = row
        try:
            response = requests.get(f"{self.base_url}/books/{book_id}")
            if response.status_code == 200:
                book = response.json()
                msg = (
                    f"Name: {book.get('name','')}\n"
                    f"Author: {book.get('author','')}\n"
                    f"Publication Date: {book.get('publication_date','')}\n"
                    f"Category: {book.get('category','')}\n"
                    f"Borrowed: {book.get('borrowed', False)}"
                )
                if book.get('borrower_name'):
                    msg += f"\nBorrower's Name: {book.get('borrower_name')}"
                if book.get('borrow_date'):
                    msg += f"\nBorrow Date: {book.get('borrow_date')}"
                if book.get('due_date'):
                    msg += f"\nDue Date: {book.get('due_date')}"
                QMessageBox.information(self, "Book Metadata", msg)
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Cannot connect to backend.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
