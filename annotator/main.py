from src.ui.ui import MainWindow
from PyQt5.QtWidgets import QApplication
import sys


DATA_PATH = "../data"
SINGLE_VIDEO = True
RANDOM_DIR = True

if __name__ == "__main__":
    # If a CLI arg is passed, use the test data
    if len(sys.argv) > 1:
        DATA_PATH = "testdata/simplecase"

    app = QApplication([])
    window = MainWindow(
            DATA_PATH,
            single_video=SINGLE_VIDEO,
            random_dir=RANDOM_DIR)

    window.show()
    app.exec_()
