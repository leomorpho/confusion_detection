import glob
import platform
import os
import subprocess
import shlex
import shutil
import shutil
import sys
import numpy as np
import multiprocessing
from PIL import Image

# This script creates a new dataset from the original dataset.
# The new dataset is simply a directory containing ALL of the
# videos from the original dataset.

# Place the original dataset in the "data/raw" directory:
# data/raw/2019-10-16-15-11-45bag_img_raw_03 etcetera

DATA = "data/raw"
NEW_DATA = "data/new_raw"
MAX_DIGITS_FRAME_NAME = 4
TMP = "data/tmp"

OPENPOSE_MACOS_INSTALL = "../openpose/build/examples/openpose/openpose.bin"
OPENPOSE_WSL_WINDOWS = "/mnt/c/Users/leona/Downloads/openpose-1.6.0-binaries-win64-only_cpu-python-flir-3d/openpose/bin/OpenPoseDemo.exe"

NUM_CORES = 3


def run_openpose(videos, run_id):
    for video in videos:
        print(video)

        # Remove extension
        frames_dir = "".join(video.split(".")[:-1])

        # Remove path to original raw dir
        frames_dir = "_".join(frames_dir.split("/")[2:])
        frames_dir = NEW_DATA + "/" + frames_dir

        # Extract frames if needed
        if not os.path.exists(frames_dir):
            os.mkdir(frames_dir)

            print(f"Extracting frames from {video}")
            command = f"ffmpeg -i {video} {frames_dir}/%{MAX_DIGITS_FRAME_NAME}d.jpeg -n"
            subprocess.call(shlex.split(command))

        images = glob.glob(f"{frames_dir}/*.jpeg")
        images.sort()

        # Keep track of frames that were processed in previous runs of the script
        already_finished = set()

        # Do not redo work from previous script runs
        for filepath in images:
            # Do not re-run OpenPose on already rendered images
            if "rendered" in filepath:
                name = ".".join(filepath.split("/")).split(".")[-2]
                name = name.split("_")[0]
                print(f"{name} already processed")
                already_finished.add(name)

        # Run OpenPose for every frame
        for index, filepath in enumerate(images):

            # Skip already rendered images
            if "rendered" in filepath:
                print("Image already rendered. Not re-rendering.")
                continue

            # Skip image if already processed in earlier run
            name = ".".join(filepath.split("/")).split(".")[-2]
            if name in already_finished:
                print(
                    "Image already processed. Not re-processing. Deleting original image {filepath}")
                os.remove(filepath)
                continue

            print(f"\nProcessing {filepath}...")

        # Hack to get OpenPose to work. Since there are too many images
        # in my directories, OpenPose crashes. Move each image to a directory
        # and then delete it. The results will be saved in the correct dir.
            tmp_for_thread = f"{TMP}/tmp{run_id}"
            if os.path.exists(tmp_for_thread):
                shutil.rmtree(tmp_for_thread)

            os.mkdir(tmp_for_thread)
            image_name = filepath.split("/")[-1]

            # Copy image to TMP directory for OpenPose to process it
            shutil.copyfile(filepath, f"{tmp_for_thread}/{image_name}")
            print(f"image_name: {image_name}")

            OPENPOSE_COMMAND = f"-model_pose COCO --image_dir {tmp_for_thread} --write_images {tmp_for_thread} --write_json {tmp_for_thread} --display 0 -number_people_max 1"
            # OPENPOSE_COMMAND = f"--image_dir {tmp_for_thread} --write_images {tmp_for_thread} --write_json {tmp_for_thread} --display 0 -number_people_max 1"

            # Run OpenPose against the TMP directory
            command = f"{OPENPOSE_MACOS_INSTALL} {OPENPOSE_COMMAND}"

            if "microsoft" in platform.uname()[3].lower():
                command = f"{OPENPOSE_WSL_WINDOWS} {OPENPOSE_COMMAND}"

            print(f"Running {command}")
            try:
                print(f"Running OpenPose for {filepath.split('/')[-1]}")
                subprocess.check_call(shlex.split(command))
            except subprocess.CalledProcessError as e:
                print(f"Failed to run OpenPose: {e}")
                sys.exit(1)

            json_file = glob.glob(f"{tmp_for_thread}/*.json")[0]
            image_file = glob.glob(f"{tmp_for_thread}/*.png")[0]

            # Copy rendered image back to data directory
            shutil.copy(json_file, frames_dir)
            picture = Image.open(image_file)
            image_name_no_extension = image_name.split(".")[0]
            picture.save(f"{frames_dir}/{image_name_no_extension}_rendered.jpeg",
                         'JPEG', optimize=True, quality=10)
            # Remove original if successful
            os.remove(filepath)
            print("Success")


if __name__ == "__main__":
    dirs = glob.glob(f"{DATA}/*")

    videos = []

    for directory in dirs:
        videos.extend(glob.glob(f"{directory}/*.mp4"))

    if not os.path.exists(NEW_DATA):
        os.mkdir(NEW_DATA)

    # Chunk videos for processing on different cores
    videos_chunked = np.array_split(videos, NUM_CORES)
    threads = []

    for i in range(NUM_CORES):
        p = multiprocessing.Process(
            target=run_openpose, args=(videos_chunked[i], i,))
        threads.append(p)
        p.start()

    for i in threads:
        p.join()

    # if "microsoft" in platform.uname()[3].lower():
    #     import winsound
    #     while True:
    #         duration = 1000  # milliseconds
    #         freq = 440  # Hz
    #         winsound.Beep(freq, duration)
    # else:
    #     # Assume we're on Macos
    #     while True:
    #         os.system(
    #             'say "all videos in the data directory have been processed"')
