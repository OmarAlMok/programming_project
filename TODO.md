# TODO List for Borrowing Name Feature

## GUI Updates (gui.py)
- [x] Add QLineEdit for borrower's name in BorrowBookDialog
- [x] Update borrow_book method to send borrower_name in the request
- [x] Update show_metadata to display borrower_name

## Backend Updates (backend.py)
- [x] Update borrow_book endpoint to accept and store borrower_name
- [x] Ensure get_book returns borrower_name in response

## Testing
- [ ] Run the application and test borrowing with name input
- [ ] Verify metadata shows borrower's name on double-click
