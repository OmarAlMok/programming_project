import multiprocessing
import time
import sys
from flask import Flask
from PyQt6.QtWidgets import QApplication

# Import the Flask app instance from backend.py
from backend import app as flask_app

# Import the main GUI window from gui.py
from gui import MainWindow

def run_server():
    """
    Run the Flask server.
    This function starts the Flask app with debug mode enabled, disables the
    reloader to avoid double server start, and listens on all available IP addresses on port 5000.
    """
    flask_app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Start the Flask server in a separate process using multiprocessing.
    # This allows the Flask server to run concurrently alongside the PyQt GUI,
    # so both can operate without blocking each other.
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()

    # Wait for 2 seconds to allow the Flask server to initialize before starting the GUI.
    time.sleep(2) 

    # Create the PyQt application instance
    qt_app = QApplication(sys.argv)

    # Create and show the main window from the GUI module
    window = MainWindow()
    window.show()

    # Start the Qt event loop; this call blocks until the GUI is closed by the user.
    exit_code = qt_app.exec()

    # When the GUI exits, terminate the Flask server process to clean up
    server_process.terminate()

    # Exit the program with the Qt application's exit code
    sys.exit(exit_code)
