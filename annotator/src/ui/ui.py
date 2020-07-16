from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.infra.processor import FrameProcessor
from src.infra.logger import log
import logging
import sys



class MainWindow(QMainWindow):
    def __init__(self, data_path):
        QMainWindow.__init__(self)

        # Initialize all other params
        self.init_widget()

        # Create frame processor
        self.frame_processor = FrameProcessor(data_path)

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

        # TODO: Create widget with frames
        # Show images in a grid

        self.setCentralWidget(QWidget())
        self.showMaximized()

    def keyPressEvent(self, event):

        label: str = None
        if event.key() == Qt.Key_0:
            label = "none"
        elif event.key() == Qt.Key_1:
            label = "not confused"
        elif event.key() == Qt.Key_2:
            label = "probably not confused"
        elif event.key() == Qt.Key_3:
            label = "uncertain"
        elif event.key() == Qt.Key_4:
            label = "probably confused"
        elif event.key() == Qt.Key_5:
            label = "confused"
        # Save label for current frames
        self.frame_processor.save(label)

        log.debug(label)

        # Load next frame
        self.frames_paths, is_new_dir = self.frame_processor.next()

        if is_new_dir:
            log.debug("Press \"Enter\" to load next directory. Press \"Escape\" to save and exit the program")
            if event.key() == Qt.Key_Enter:
                self.showing_frames = True
                # continue
            if event.key() == Qt.Key_Escape:
                self.close()
