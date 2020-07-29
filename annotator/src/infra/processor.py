import glob
import logging
import sys
import os
import subprocess
import shlex
import json
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

    def __init__(self, data_path, processed_path=PROCESSED):
        self.data_path = data_path

        if not os.path.exists(data_path):
            raise Exception("Import path does not exist")

        if not os.path.exists(f"{data_path}/{RAW}"):
            raise Exception("\"raw\" data path does not exist")

        if not os.path.exists(f"{data_path}/{processed_path}"):
            os.mkdir(f"{data_path}/{processed_path}")

        raw_dirs = glob.glob(f"{data_path}/{RAW}/*")
        processed_dirs = glob.glob(f"{data_path}/{processed_path}/*")

        self.queue = raw_dirs
        log.info(f"Queue length: {len(self.queue)}")
        log.info(f"First in queue: {self.queue[:3]}")

        # Build queue of unprocessed (unlabeled) directories
        # It's O^2 time but we don't care...
        for raw_dir in raw_dirs:
            raw_dir_name = raw_dir.split("/")[-1].split(".")[0]
            for processed_dir in processed_dirs:
                processed_dir_name = processed_dir.split("/")[-1]
                if processed_dir_name == raw_dir_name:
                    queue.remove(processed_dir_name)

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
            json.dump(self.results, f)

    def next(self) -> [List[str], bool]:
        """
        Load next frame and if no next frames, load next directory.
        Save on every frame.

        :return: true if next frame is from a new directory from the queue
        """
        log.debug(f"current directory: {self.curr_dir}")

        frames = self.next_frames(self.curr_dir, self.curr_frame)
        log.debug(
            f"number of frames: {len(frames)}, current frame: {self.curr_frame}")

        if len(frames) > 0:
            self.curr_frame += 1

        self.save_to_disk()

        return frames

    def prev(self) -> [List[str]]:
        """
        Load prev frame and if no prev frame, return empty list
        """

        # If there is no prev frame
        if self.curr_frame == 1:
            return []

        self.curr_frame -= 1
        frames_paths = []

        dirs_paths = self.get_all_dir_paths_in_dir(self.curr_dir)

        # Pad next frame with zeroes so it's MAX_DIGITS_FRAME_NAME digits wide
        frame_number = f"{self.curr_frame}".zfill(MAX_DIGITS_FRAME_NAME)

        for path in dirs_paths:
            # Frames directory has name of video minus extension
            prev_frame_path = f"{path}/{frame_number}.jpeg"
            if os.path.exists(prev_frame_path):
                frames_paths.append(prev_frame_path)

        return frames_paths

    def next_directory(self, extract_frames=True) -> bool:
        """
        :param extract_frames: can turn off for testing

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

        # Extract frames from all videos
        video_paths = self.get_all_video_paths_in_dir(self.curr_dir)

        if extract_frames:
            for video_path in video_paths:
                # Extract frames to sibling directory of video
                # (place dir next to vid)
                self.extract_all_frames_from_video(video_path)
        return True

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
        log.debug(
            f"Creating new directory {frames_dir_path} for video {video_path}")

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
        Return paths to next frames and current frame count
        """
        dirs_paths = cls.get_all_dir_paths_in_dir(parent_dir)

        frames_paths = []

        # Pad next frame with zeroes so it's MAX_DIGITS_FRAME_NAME digits wide
        frame_number = f"{curr_frame_count}".zfill(MAX_DIGITS_FRAME_NAME)

        for path in dirs_paths:
            # Frames directory has name of video minus extension
            next_frame_path = ""
            try:
                next_frame_path = glob.glob(f"{path}/{frame_number}*")[0]
            except IndexError:
                # Try to get all the frames from a folder, even if for some
                # videos the frames ran out.
                next_frame_path = None

            if next_frame_path:
                frames_paths.append(next_frame_path)

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

    @staticmethod
    def get_all_dir_paths_in_dir(path) -> List[str]:
        """
        Return the paths to every video in a directory
        """
        return [f"{path}/{i}" for i in os.listdir(path) if os.path.isdir(f"{path}/{i}")]

    def extract_frames_for_all_dirs(self):
        # Add current directory to queue
        dir_list = self.queue
        dir_list.append(self.curr_dir)

        for directory in dir_list:
            video_paths = self.get_all_video_paths_in_dir(directory)
            for video_path in video_paths:
                # Extract frames to sibling directory of video (place dir next to vid)
                self.extract_all_frames_from_video(video_path)
        log.info("Finished extracting frames for all videos from all directories")
