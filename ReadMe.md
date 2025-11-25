### This ReadMe file is a guide to the workings of the Online Library Program: how it is structured, functions and tricks to navigate through it with ease, and an insight to its inner workings.

## The Online Library Program is a desktop application built with:
- PyQt6: Graphical User Interface (GUI)
- Flask: Backendd web server handling all book operations
- JSON file : Database storing all book information
- Multiprocessing: Runs Flask and GUI simultaneously 

# The program lets you:
1. Add books
2. Delete books
3. Borrow and return books
4. Filter and search books
5. View a book's metadata by double-clicking

# Installation
- To install and run the program, make sure you have python installed. Then, install PyGt6 and Flask.

# How to run
- run main.py

# How the program starts:
When you run main.py, the flask server gets activated at http://localhost:5000. Then, after 2 seconds, the gui is activated. When the gui is closed the server terminates.

# Architecture
- The user has acces to the GUI. 
- The GUI sends HTTP requests to the Flask backend.
- The backend handles all operations- adding, deleting, borrowing, returning, and filtering books. 
- Book data is saved to and loaded from the JSON database (data.db)

# Structure
- main.py: Starts the backedn and the GUI.
- gui.py: Handles the GUI.
- backend.py: Flask server managing database operations.
- data.db: JSON database storing all book information
- README.md: Documentation file

# HTTP Endpoints
1. GET /books: Retrieve all book
2. POST /books: Add a new book
3. DELETE /books/<id>: Delete a book
4. POST /books/<id>/borrow: Borrow a book
5. POST /books/<id>/return: Return a book
6. GET /books/<id>: Get information about a specific book

# Limitations
- The program must run locally
- Any actions that take place in the GUI takes 2-4 seconds to be uploaded
- data.db is stored as plain JSON and is not encrypted.
