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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Book")
        layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.date_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.category_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Publication Date:", self.date_edit)
        layout.addRow("Author:", self.author_edit)
        layout.addRow("Category:", self.category_edit)
        self.ok_btn = QPushButton("Add")
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

        # Search and filter
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name...")
        self.search_btn = QPushButton("Search")
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.addItem("Fiction")
        self.category_combo.addItem("Non-Fiction")
        self.category_combo.addItem("Science")
        self.category_combo.addItem("History")
        self.category_combo.addItem("Philosophy")
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

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Author", "Publication Date", "Category", "Status"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Buttons
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

        # Connect signals
        self.search_btn.clicked.connect(self.search)
        self.category_combo.currentTextChanged.connect(self.filter_category)
        self.borrowed_combo.currentTextChanged.connect(self.filter_borrowed)
        self.refresh_btn.clicked.connect(self.load_books)
        self.add_btn.clicked.connect(self.add_book)
        self.delete_btn.clicked.connect(self.delete_book)
        self.borrow_btn.clicked.connect(self.borrow_book)
        self.return_btn.clicked.connect(self.return_book)
        self.table_widget.cellDoubleClicked.connect(self.show_metadata)

        self.load_books()

    def load_books(self):
        try:
            response = requests.get(f"{self.base_url}/books")
            if response.status_code == 200:
                books = response.json()
                self.table_widget.setRowCount(len(books))
                for i, book in enumerate(books):
                    self.table_widget.setItem(i, 0, QTableWidgetItem(book['name']))
                    self.table_widget.setItem(i, 1, QTableWidgetItem(book['author']))
                    self.table_widget.setItem(i, 2, QTableWidgetItem(book['publication_date']))
                    self.table_widget.setItem(i, 3, QTableWidgetItem(book['category']))
                    status = "Borrowed" if book['borrowed'] else "Available"
                    self.table_widget.setItem(i, 4, QTableWidgetItem(status))
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def search(self):
        name = self.search_edit.text().strip()
        if name:
            try:
                response = requests.get(f"{self.base_url}/books", params={'name': name})
                if response.status_code == 200:
                    books = response.json()
                    self.table_widget.setRowCount(len(books))
                    for i, book in enumerate(books):
                        self.table_widget.setItem(i, 0, QTableWidgetItem(book['name']))
                        self.table_widget.setItem(i, 1, QTableWidgetItem(book['author']))
                        self.table_widget.setItem(i, 2, QTableWidgetItem(book['publication_date']))
                        self.table_widget.setItem(i, 3, QTableWidgetItem(book['category']))
            except requests.exceptions.RequestException:
                QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def filter_category(self):
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
                self.table_widget.setRowCount(len(books))
                for i, book in enumerate(books):
                    self.table_widget.setItem(i, 0, QTableWidgetItem(book['name']))
                    self.table_widget.setItem(i, 1, QTableWidgetItem(book['author']))
                    self.table_widget.setItem(i, 2, QTableWidgetItem(book['publication_date']))
                    self.table_widget.setItem(i, 3, QTableWidgetItem(book['category']))
                    status = "Borrowed" if book['borrowed'] else "Available"
                    self.table_widget.setItem(i, 4, QTableWidgetItem(status))
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def filter_borrowed(self):
        self.filter_category()

    def add_book(self):
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
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            book_id = current_row
            try:
                response = requests.post(f"{self.base_url}/books/{book_id}/borrow")
                if response.status_code == 200:
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", response.json().get('error', 'Failed to borrow book'))
            except requests.exceptions.RequestException:
                QMessageBox.warning(self, "Error", "Cannot connect to backend.")

    def return_book(self):
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
        book_id = row
        try:
            response = requests.get(f"{self.base_url}/books/{book_id}")
            if response.status_code == 200:
                book = response.json()
                msg = f"Name: {book['name']}\nAuthor: {book['author']}\nPublication Date: {book['publication_date']}\nCategory: {book['category']}\nBorrowed: {book['borrowed']}"
                QMessageBox.information(self, "Book Metadata", msg)
        except requests.exceptions.RequestException:
            QMessageBox.warning(self, "Error", "Cannot connect to backend.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
