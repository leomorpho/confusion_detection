from typing import Tuple, List
import math
import logging
import numpy as np


log = logging.getLogger()
log.setLevel(logging.DEBUG)


MAX_DROPPED_FRAMES = 3
MIN_DIST = 40


def centroid(frame):
    """
    Find the centroid for an array points (x, y)
    """
    # Create 2D array
    frame = frame[1:]
    frame_positions = np.array(list(zip(frame, frame[1:]))[::2])

    length = frame_positions.shape[0]
    sum_x = np.sum(frame_positions[:, 0])
    sum_y = np.sum(frame_positions[:, 1])
    return sum_x/length, sum_y/length


def dist(pair1: Tuple[float, float], pair2: Tuple[float, float]) -> float:
    """
    Return distance between 2 points (x, y) as a single scalar
    """
    x_dist = abs(pair1[0] - pair2[0])
    y_dist = abs(pair2[1] - pair2[1])

    dist = math.sqrt(x_dist**2 + y_dist**2)

    log.debug(f"Distance: {dist}")

    return dist


def check_frames(raw_sequences: List[List[List[float]]]):
    """
    Check for frames which have OpenPose data that does not fit
    with the previous frame. These errors are introduced because
    OpenPose was only asked to identify one person. Research
    assistants in the background, as well as the Pepper robot
    sometimes wrongly get detected as the participants.

    If there are less than a certain number of faulty frames, the
    sequences separated by these faulty frames should be stitched back
    together. Else, separate them as two distinct sequences.

    :param raw_sequences: the sequences read from file
    :type  raw_sequences: List[List[List[float]]]

    :returns new_sequences: the processed sequences
    :type    new_sequences: List[List[List[float]]]
    """
    # new sequences are the cleaned up sequences. If less than
    # MAX_DROPPED_FRAMES were dropped, the sequences will be stiched,
    # and new_sequences will contain a single sequence.
    new_sequences = [[]]

    for raw_sequence in raw_sequences[:1]:

        # Keep track of the number of new sequences created
        sequences_count = 0

        # Keep track of centroid from last frame
        last_frame_centroid = None
        # If less than MAX_DROPPED_FRAMES are dropped,
        # the sequences will be stitched.
        num_dropped_frames = 0

        for frame in raw_sequence:
            # Create new sequence if the maximum amount
            # of dropped frames was reached.
            if len(frame) < 2:
                # Label or OpenPose data is missing
                continue
            if num_dropped_frames >= MAX_DROPPED_FRAMES:
                log.debug(f"Max dropped frames reached, creating new sequence.")
                new_sequences.append([])
                sequences_count += 1
                num_dropped_frames = 0
                new_sequences[sequences_count].append(frame)
            elif not last_frame_centroid:
                log.debug(f"Appending first frame.")
                # this frame is the first in the sequence
                new_sequences[sequences_count].append(frame)
                last_frame_centroid = centroid(frame)
            else:
                current_centroid = centroid(frame)
                if dist(current_centroid, last_frame_centroid) < MIN_DIST \
                        and frame[0] != 0:
                    # Current and previous frames are likely of the
                    # same participant.
                    new_sequences[sequences_count].append(frame)
                else:
                    log.debug("Frame distance too great, dropping.")
                    # This is a dud. Don't use it. It either has
                    # no participant (label = 0), or contains a different
                    # person than the wanted participant.
                    num_dropped_frames += 1

                # Update position of last frame to current frame
                last_frame_centroid = current_centroid

    return new_sequences
