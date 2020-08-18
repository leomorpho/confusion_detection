import glob
import logging
import sys
import os
import subprocess
import shlex
import json
import random
import getpass
from typing import List
from src.infra.logger import log

RAW = "new_raw"
PROCESSED = "processed"

# This is the maximum number of digits which can be in a frame name. This
# means there are a maximum of 1000 frames per video
MAX_DIGITS_FRAME_NAME = 4


class FrameProcessor:
    """
    Searches the import and processed data paths. Any single directory in
    the import path which has not been processed yet is added to the queue.
    """

    def __init__(self, data_path, processed_path=PROCESSED, random_dir=False):
        self.data_path = data_path

        if not os.path.exists(data_path):
            raise Exception("Import path does not exist")

        if not os.path.exists(f"{data_path}/{RAW}"):
            raise Exception(f"'{data_path}/{RAW}' data path does not exist")

        if not os.path.exists(f"{data_path}/{processed_path}"):
            os.mkdir(f"{data_path}/{processed_path}")

        raw_dirs = glob.glob(f"{data_path}/{RAW}/*")
        processed_dirs = glob.glob(f"{data_path}/{processed_path}/*")
        processed_dirs = [i.split("/")[-1].split(".")[0]
                          for i in processed_dirs]

        self.queue = raw_dirs

        # Build queue of unprocessed (unlabeled) directories
        # It's O^2 time but we don't care...
        for raw_dir in raw_dirs:
            raw_dir_name = raw_dir.split("/")[-1].split(".")[0]
            for processed_dir in processed_dirs:
                if processed_dir == raw_dir_name:
                    log.info(
                        f"Already processed. Removing dir {processed_dir} from queue")
                    self.queue.remove(raw_dir)

        tmp_queue = []
        # Remove if currently being processed by OpenPose.
        for to_process in self.queue:
            images = glob.glob(f"{to_process}/*.jpeg")
            finished = True

            for image in images:
                if "render" not in image:
                    finished = False
                    break

            if not finished:
                tmp_queue.append(to_process)

        self.queue = tmp_queue

        if random_dir:
            # Shuffles in place
            random.shuffle(self.queue)
            print(self.queue)

        log.info(f"Queue length: {len(self.queue)}")
        log.info(f"First in queue: {self.queue[:3]}")

        # Keep track of current directory of raw data
        self.curr_dir = self.queue.pop()

        # Frame counter
        self.curr_frame = 1

        # Results dictionnary, where each label for each frame is stored
        self.results = dict()

    def save(self, label: str):
        """
        Save the label for a frame. This method does not save to disk.
        """
        # somewhere it should not be increased.
        self.results[self.curr_frame - 1] = label

    def save_to_disk(self):
        """
        Persist results to disk
        """

        # Don't save if empty
        if len(self.results) == 0:
            return

        filename = self.curr_dir.split("/")[-1].split(".")[0]
        result_path = f"{self.data_path}/{PROCESSED}/{filename}.json"
        with open(result_path, "w") as f:
            # Remove ending ".mp4" extension and starting slash
            frames_dir = self.curr_dir.split("/")[-1]
            data = {
                "annotator": getpass.getuser(),
                "framesDirectory": frames_dir,
                "labels": self.results
            }
            json.dump(data, f)

    def next(self) -> str:
        """
        Load next frame and if no next frame, load next directory.
        Save on every frame.

        :return: true if next frame is from a new directory from the queue
        """
        log.debug(f"current directory: {self.curr_dir}")

        frame = self.next_frame(self.curr_dir, self.curr_frame)

        if frame:
            self.curr_frame += 1

        self.save_to_disk()

        return frame

    def prev(self) -> str:
        """
        Load prev frame and if no prev frame, return empty list
        """
        # If there is no prev frame
        if self.curr_frame == 1:
            return None

        self.curr_frame -= 1

        # Pad next frame with zeroes so it's MAX_DIGITS_FRAME_NAME digits wide
        frame_number = f"{self.curr_frame}".zfill(MAX_DIGITS_FRAME_NAME)

        # Frames directory has name of video minus extension
        prev_frame_path = glob.glob(
            f"{self.curr_dir}/*{frame_number}*.jpeg")[0]
        if os.path.exists(prev_frame_path):
            return prev_frame_path

        return None

    def next_directory(self, single_video=False) -> bool:
        """
        :param single_video: use only 1 video for annotation.
            Do not use all videos. This is usefull if videos have
            inconsistent frame rates.

        :return: whether there is a next directory or not
        """
        # Load next directory and extract images for directory coming
        # after this one (ffmpeg takes some time)
        log.info("Loading next directory")

        # Do not catch exception here, parent will catch it
        try:
            self.curr_dir = self.queue.pop()
        except IndexError:
            self.curr_dir = None
            return False

        self.curr_frame = 1
        self.results = dict()

        log.info(f"New current directory is {self.curr_dir}")

        return True

    @classmethod
    def next_frame(cls, parent_dir, curr_frame_count) -> List[str]:
        """
        Return paths to next frames and current frame count
        """

        # Pad next frame with zeroes so it's MAX_DIGITS_FRAME_NAME digits wide
        frame_number = f"{curr_frame_count}".zfill(MAX_DIGITS_FRAME_NAME)

        # Frames directory has name of video minus extension
        next_frame_path = ""
        try:
            next_frame_path = glob.glob(
                f"{parent_dir}/*{frame_number}*.jpeg")[0]
        except IndexError:
            # Try to get all the frames from a folder, even if for some
            # videos the frames ran out.
            next_frame_path = None

        log.info(f"Next frame: {next_frame_path}")
        return next_frame_path

    @staticmethod
    def get_all_video_paths_in_dir(path) -> List[str]:
        """
        Return the paths to every video in a directory
        """
        video_paths = glob.glob(f"{path}/*.mp4")
        if video_paths:
            log.debug(f"Videos found: {video_paths}")
        else:
            log.debug(f"No videos found at path {path}")

        return video_paths

    @staticmethod
    def get_all_dir_paths_in_dir(path) -> List[str]:
        """
        Return the paths to every video in a directory
        """
        dirs = []
        for i in os.listdir(path):
            if os.path.isdir(f"{path}/{i}") and "pepper" not in i.lower():
                dirs.append(f"{path}/{i}")

        return dirs
