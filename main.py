import multiprocessing
import time
import sys
from flask import Flask
from PyQt6.QtWidgets import QApplication

# Import the app from flask.py
from backend import app as flask_app

# Import the GUI from gui.py
from gui import MainWindow

def run_server():
    flask_app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Start Flask server in a separate process
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()

    # Wait for server to start
    time.sleep(2)

    # Start PyQt GUI
    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = qt_app.exec()

    # Terminate server when GUI closes
    server_process.terminate()
    sys.exit(exit_code)
