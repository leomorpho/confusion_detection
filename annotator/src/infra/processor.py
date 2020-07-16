import glob
import logging
import sys
import os
import subprocess
import shlex
from typing import List
from src.infra.logger import log

RAW = "raw"
PROCESSED = "processed"

# This is the maximum number of digits which can be in a frame name. This
# means there are a maximum of 1000 frames per video
MAX_DIGITS_FRAME_NAME = 4

class FrameProcessor:
    """
    Searches the import and processed data paths. Any single directory in
    the import path which has not been processed yet is added to the queue.
    """
    def __init__(self, data_path):
        self.data_path = data_path

        if not os.path.exists(data_path):
            raise Exception("Import path does not exist")

        if not os.path.exists(f"{data_path}/{RAW}"):
            raise Exception("\"raw\" data path does not exist")

        if not os.path.exists(f"{data_path}/{PROCESSED}"):
            os.mkdir(f"{data_path}/{PROCESSED}")

        raw_dirs = glob.glob(f"{data_path}/{RAW}/*")
        processed_dirs = glob.glob(f"{data_path}/{PROCESSED}/*")

        self.queue = raw_dirs

        # Build queue of unprocessed (unlabeled) directories
        # It's O^2 time but we don't care...
        for raw_dir in raw_dirs:
            raw_dir_name = raw_dir.split("/")[-1].split(".")[0]
            for processed_dir in processed_dirs:
                processed_dir_name = processed_dir.split("/")[-1]
                if processed_dir_name == raw_dir_name:
                    queue.remove(processed_dir_name)

        # Keep track if current dir was processed to completion
        self.directory_processed = False

        # Keep track of current directory of raw data
        self.curr_dir = None

        # Frame counter
        self.curr_frame = 0

    def save(self, label: str):
        """
        Save the label for a frame
        """
        pass

    def next(self) -> [List[str], bool]:
        """
        Load next frame and if no next frames, load next directory.

        :return: true if next frame is from a new directory from the queue
        """
        is_new_dir = False

        frames = self.next_frames(self.curr_dir, self.curr_frame)

        if not frames:
            # Load next directory and extract images for directory coming
            # after this one (ffmpeg takes some time)
            try:
                self.curr_dir = self.queue.pop()
            except IndexError:
                return [], False

                return
            log.debug(f"New current directory is {self.curr_dir}")

            # Extract frames from all videos
            video_paths = self.get_all_video_paths_in_dir(self.curr_dir)
            for video_path in video_paths:
                # Extract frames to sibling directory of video (place dir next to vid)
                self.extract_all_frames_from_video(video_path)

            is_new_dir = True

        return frames, is_new_dir


    @staticmethod
    def extract_all_frames_from_video(video_path):
        """
        Extract all frames from a video.

        :param video_path: video to extract frames from
        :param frames_path: dir to extract frames to
        """
        # Create directory name from video name
        dir_name = video_path.split("/")[-1].split(".")[0]
        log.debug(f"About to extract frames for video {video_path}")

        parent_dir = video_path.split("/")
        parent_dir = "/".join(parent_dir[:-1])
        frames_dir_path = f"{parent_dir}/{dir_name}"
        log.debug(f"Creating new directory {frames_dir_path} for video {video_path}")

        if os.path.exists(frames_dir_path):
            num_images = len(glob.glob(f"{frames_dir_path}/*"))
            if num_images > 0:
                log.debug("Frames directory for video already exists")
                return
        else:
            os.makedirs(frames_dir_path)

        command = f"ffmpeg -i {video_path} {frames_dir_path}/%{MAX_DIGITS_FRAME_NAME}d.jpeg -n"
        subprocess.call(shlex.split(command))
        log.debug(f"Extracted frames for video {video_path}")

    @classmethod
    def next_frames(cls, parent_dir, curr_frame_count) -> List[str]:
        """
        Return paths to next frames
        """
        video_paths = cls.get_all_video_paths_in_dir(parent_dir)

        frames_paths = []

        # Pad next frame with zeroes so it's MAX_DIGITS_FRAME_NAME digits wide
        next_frame_count = f"{curr_frame_count + 1}".zfill(MAX_DIGITS_FRAME_NAME)

        for path in video_paths:
            next_frame_path = glob.glob(f"{path}/*{next_frame_count}*")
            frames_paths.extend(next_frame_path)

        log.debug(f"Next frames are at {frames_paths}")
        return frames_paths


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
