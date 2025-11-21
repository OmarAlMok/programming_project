# Online Library Project TODO

- [x] Update data.db to store book metadata (Name, Publication date, Author, Category, Borrowed status)
- [x] Update Flask backend endpoints to match requirements:
  - [x] 1. List all available media (GET /books, filter borrowed=false)
  - [x] 2. List available in specific category (GET /books?category=<cat>)
  - [x] 3. Search exact name (GET /books?name=<name>)
  - [x] 4. Display metadata (GET /books/<id>)
  - [x] 5. Create new media (POST /books)
  - [x] 6. Delete specific media (DELETE /books/<id>)
- [x] Update PyQt frontend to match requirements:
  - [x] 1. Display list of all borrowable media
  - [x] 2. Category dropdown for available in category
  - [x] 3. Exact name search input
  - [x] 4. Click to display metadata
  - [x] 5. Button to create new media
  - [x] 6. Click to delete media
- [x] Test integration: Run Flask and GUI, verify functionality
- [x] Add web interface to Flask: icons/buttons for search, create, delete, borrow
- [x] Add borrowed sorting in Flask and GUI: filter to view borrowed or available items
