from src.ui.ui import MainWindow
from PyQt5.QtWidgets import QApplication
import sys


DATA_PATH = "../data"

if __name__ == "__main__":
    # If a CLI arg is passed, use the test data
    if len(sys.argv) > 1:
        DATA_PATH = "test_data"

    app = QApplication([])
    window = MainWindow(DATA_PATH)
    window.show()
    app.exec_()
