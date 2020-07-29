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

    def __init__(self, image_paths=None, images_per_row=4):
        super().__init__()

        self.img_not_available_path = './media/no_image_available.png'
        grid = QGridLayout(self)

        self.label1 = QLabel()
        self.label2 = QLabel()
        self.label3 = QLabel()
        self.label4 = QLabel()

        im = QPixmap(self.img_not_available_path)
        self.label1.setPixmap(im)
        self.label2.setPixmap(im)
        self.label3.setPixmap(im)
        self.label4.setPixmap(im)
        grid.addWidget(self.label1, 0, 0)
        grid.addWidget(self.label2, 0, 1)
        grid.addWidget(self.label3, 1, 0)
        grid.addWidget(self.label4, 1, 1)
        self.setLayout(grid)

    def update_images(self, paths):
        if len(paths) >= 1 and os.path.exists(paths[0]):
            im1 = QPixmap(paths[0])
            im1 = im1.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label1.setPixmap(im1)
        else:
            im = QPixmap(self.img_not_available_path)
            im = im.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label1.setPixmap(im)

        if len(paths) >= 2 and os.path.exists(paths[1]):
            im2 = QPixmap(paths[1])
            im2 = im2.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label2.setPixmap(im2)
        else:
            im = QPixmap(self.img_not_available_path)
            im = im.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label2.setPixmap(im)

        if len(paths) >= 3 and os.path.exists(paths[2]):
            im3 = QPixmap(paths[2])
            im3 = im3.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label3.setPixmap(im3)
        else:
            im = QPixmap(self.img_not_available_path)
            im = im.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label3.setPixmap(im)

        if len(paths) >= 4 and os.path.exists(paths[3]):
            im4 = QPixmap(paths[3])
            im4 = im4.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label4.setPixmap(im4)
        else:
            im = QPixmap(self.img_not_available_path)
            im = im.scaled(self.label1.size(), Qt.KeepAspectRatio)
            self.label4.setPixmap(im)


class Buttons(QWidget):
    """
    Display label button in a line
    """

    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout(self)
        hbox.addWidget(QLabel("(1) No"))
        hbox.addWidget(QLabel("(2) Unlikely"))
        hbox.addWidget(QLabel("(3) Ambivalent"))
        hbox.addWidget(QLabel("(4) Likely"))
        hbox.addWidget(QLabel("(5) Confused"))
        hbox.addWidget(QLabel("(R arrow) previous"))
        hbox.addWidget(QLabel("(L arrow) next"))

        self.setLayout(hbox)


class CentralWidget(QWidget):
    def __init__(self, images_paths=None):
        super().__init__()
        self.image_widget = Images(images_paths)

        # Top info is the title of processed folder and the number of
        # cameras being shown (out of total)
        self.processed_dir_name = QLabel()
        self.num_camera_widget = QLabel()

        buttons_widget = Buttons()

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.processed_dir_name)
        vbox.addWidget(self.num_camera_widget)
        vbox.addWidget(self.image_widget)
        vbox.addWidget(buttons_widget)
        self.setLayout(vbox)
        self.num_cameras = None

    def update_images(self, images_paths=None, processed_dir=None):
        """
        Updates the images in the UI
        """
        # Keep track of max number of cameras
        if not self.num_cameras:
            self.num_cameras = len(images_paths)
        self.image_widget.update_images(images_paths)
        self.processed_dir_name.setText(f"Processing: {processed_dir}")
        self.num_camera_widget.setText(
            f"Showing frames from {len(images_paths)}/{self.num_cameras} cameras")


class MainWindow(QMainWindow):
    def __init__(self, data_path):
        QMainWindow.__init__(self)

        # Create frame processor
        self.frame_processor = FrameProcessor(data_path)

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

        # Extract frames QAction
        frames_action = QAction("Extract all frames", self)
        frames_action.triggered.connect(self.extract_frames_for_all_dirs)
        self.file_menu.addAction(frames_action)

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
            label = "probably not confused"
        elif event.key() == Qt.Key_3:
            label = "uncertain"
        elif event.key() == Qt.Key_4:
            label = "probably confused"
        elif event.key() == Qt.Key_5:
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
        frames_paths = self.frame_processor.next()

        if not frames_paths:
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
                next_dir = self.frame_processor.next_directory()

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

                frames_paths = self.frame_processor.next()
            if choice == QMessageBox.No:
                # Undo next frame
                _ = self.frame_processor.prev()
                pass

        if frames_paths:
            # Update UI
            self.central_widget.update_images(
                frames_paths,
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
            self.central_widget.update_images(
                frames,
                self.frame_processor.curr_dir)

    def save_frame(self, label):
        """
        Abstract frame_processor
        """
        self.frame_processor.save(label)

    def extract_frames_for_all_dirs(self):
        self.frame_processor.extract_frames_for_all_dirs()
