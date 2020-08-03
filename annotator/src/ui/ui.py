from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.infra.processor import FrameProcessor
from src.infra.logger import log
import logging
import sys
import os


class Images(QWidget):
    """
    Display images in a grid
    """
    # TODO: for future users, this display logic requires a refactor
    # to make it more programatic. This was done for speed of implementation
    # and is not ideal nor clear. Different number of images should be able to show
    # and adapt dynamically.

    def __init__(self, image_path=None):
        super().__init__()

        self.img_not_available_path = './media/no_image_available.png'
        grid = QGridLayout(self)

        self.label1 = QLabel()

        im = QPixmap(self.img_not_available_path)
        self.label1.setPixmap(im)
        grid.addWidget(self.label1)
        self.setLayout(grid)

    def update_image(self, path):
        im1 = QPixmap(path)
        im1 = im1.scaled(self.label1.size(), Qt.KeepAspectRatio)
        self.label1.setPixmap(im1)


class Buttons(QWidget):
    """
    Display label button in a line
    """

    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout(self)
        hbox.addWidget(QLabel("(0) No test subject"))
        hbox.addWidget(QLabel("(1) Not confused"))
        hbox.addWidget(QLabel("(2) Uncertain"))
        hbox.addWidget(QLabel("(3) Confused"))
        hbox.addWidget(QLabel("(R arrow) previous (won't affect data)"))
        hbox.addWidget(QLabel("(L arrow) next (won't affect data)"))

        self.setLayout(hbox)
        self.setMaximumHeight(60)


class CentralWidget(QWidget):
    def __init__(self, images_paths=None):
        super().__init__()
        self.image_widget = Images(images_paths)

        # Top info is the title of processed folder and the number of
        # cameras being shown (out of total)
        self.processed_dir_name = QLabel()
        self.processed_dir_name.setFixedHeight(10)
        self.num_camera_widget = QLabel()
        self.num_camera_widget.setFixedHeight(10)

        buttons_widget = Buttons()

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.processed_dir_name)
        vbox.addWidget(self.num_camera_widget)
        vbox.addWidget(self.image_widget)
        vbox.addWidget(buttons_widget)
        self.setLayout(vbox)
        self.num_cameras = None

    def update_image(self, images_paths=None, processed_dir=None):
        """
        Updates the images in the UI
        """
        # Keep track of max number of cameras
        if not self.num_cameras:
            self.num_cameras = len(images_paths)
        self.image_widget.update_image(images_paths)
        self.processed_dir_name.setText(f"Processing: {processed_dir}")
        self.num_camera_widget.setText(
            f"Showing frames from {len(images_paths)}/{self.num_cameras} cameras")


class MainWindow(QMainWindow):
    def __init__(self,
                 data_path: str,
                 single_video: bool = False,
                 random_dir=False):

        QMainWindow.__init__(self)

        # If frame rates are inconsistent among videos, use only one video
        self.single_video = single_video

        # Create frame processor
        self.frame_processor = FrameProcessor(data_path, random_dir=random_dir)

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

        self.central_widget = CentralWidget()

        self.setCentralWidget(self.central_widget)
        self.showMaximized()
        self.next_frame()

    def keyPressEvent(self, event):

        previous_frame = False
        next_frame = False
        label: str = None

        if event.key() == Qt.Key_0:
            label = "none"
        elif event.key() == Qt.Key_1:
            label = "not confused"
        elif event.key() == Qt.Key_2:
            label = "uncertain"
        elif event.key() == Qt.Key_3:
            label = "confused"
        elif event.key() == Qt.Key_Left:
            previous_frame = True
        elif event.key() == Qt.Key_Right:
            next_frame = True

        if label:
            log.debug(f"Assigned label: {label}")
            # Save label for current frames
            self.save_frame(label)
            self.next_frame()
        elif previous_frame:
            self.prev_frame()
        elif next_frame:
            self.next_frame()

    def next_frame(self):
        # Load next frame
        frames_path = self.frame_processor.next()

        if not frames_path:
            msg = QMessageBox()
            msg.setWindowTitle("Finished current directory")
            msg.setText("Save and go on to next directory?")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msg.setDefaultButton(QMessageBox.Yes)
            msg.setDetailedText("Save and go to next directoryi (YES), " +
                                "or stay in current directory (NO).")

            choice = msg.exec_()

            if choice == QMessageBox.Yes:
                self.frame_processor.save_to_disk()
                next_dir = self.frame_processor.next_directory(
                    single_video=self.single_video)

                if not next_dir:
                    log.info("Finished all directories")
                    msg = QMessageBox()
                    msg.setWindowTitle("Finished all directories")
                    msg.setText("There are no unprocessed directories left")
                    msg.setIcon(QMessageBox.Question)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    choice = msg.exec_()
                    if choice == QMessageBox.Ok:
                        self.close()
                        sys.exit(1)

                frames_path = self.frame_processor.next()
            if choice == QMessageBox.No:
                # Undo next frame
                _ = self.frame_processor.prev()
                pass

        if frames_path:
            # Update UI
            self.central_widget.update_image(
                frames_path,
                self.frame_processor.curr_dir)

    def prev_frame(self):
        """
        Get the previous frame if there is any. Does not change the processed data.
        """
        log.info("Get previous frame")
        frames = self.frame_processor.prev()

        if frames:

            log.debug(f"prev: {frames}")

            # Update UI
            self.central_widget.update_image(
                frames,
                self.frame_processor.curr_dir)

    def save_frame(self, label):
        """
        Abstract frame_processor
        """
        self.frame_processor.save(label)
