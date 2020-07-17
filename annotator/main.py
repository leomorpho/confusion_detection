from src.ui.ui import MainWindow
from PyQt5.QtWidgets import QApplication

DATA_PATH = "../data"

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow(DATA_PATH)
    window.show()
    app.exec_()
