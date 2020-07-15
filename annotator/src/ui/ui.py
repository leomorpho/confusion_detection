from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.audio_file_path = None

        # Initialize all other params
        self.init_widget()

    def init_widget(self):
        self.setWindowTitle("Annotator")

        # Menu
        self.menu = self.menuBar()
        self.menu.setNativeMenuBar(False)
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # Window dimensions
        geometry = qApp.desktop().availableGeometry(self)

        self.setCentralWidget(QWidget())
        self.showMaximized()
