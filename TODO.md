# TODO: Generate Pytest Tests for Frontend (gui.py)

- [x] Import necessary modules in tests.py (pytest, PyQt6.QtWidgets, unittest.mock, etc.)
- [x] Create pytest fixture for QApplication setup/teardown
- [x] Write test functions for AddBookDialog:
  - Test dialog initialization
  - Test input field presence
  - Test accept behavior
- [x] Write test functions for BorrowBookDialog:
  - Test dialog initialization
  - Test input field
  - Test accept behavior
- [x] Write test functions for MainWindow:
  - Test populate_table method with sample book data
  - Mock and test network-dependent methods: load_books, search, filter_books, add_book, delete_book, borrow_book, return_book, show_metadata
- [x] Use mocking for requests.get, requests.post, requests.delete to simulate backend responses
- [x] Ensure tests are isolated and do not require running backend or GUI display
- [x] Run pytest on tests.py to execute the tests
- [x] Verify pytest and PyQt6 are installed; install if necessary
- [x] Check for test failures and adjust accordingly
