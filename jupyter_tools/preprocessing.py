from typing import Tuple, List
import math
import logging
import numpy as np
from sklearn import preprocessing


log = logging.getLogger()
log.setLevel(logging.DEBUG)


MAX_DROPPED_FRAMES = 3
MIN_DIST = 60
MIN_SEQUENCE_LEN = 5


def _centroid(frame):
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


def _dist(pair1: Tuple[float, float], pair2: Tuple[float, float]) -> float:
    """
    Return distance between 2 points (x, y) as a single scalar
    """
    x_dist = abs(pair1[0] - pair2[0])
    y_dist = abs(pair2[1] - pair2[1])

    dist = math.sqrt(x_dist**2 + y_dist**2)

    # log.debug(f"Distance: {dist}")

    return dist


def stitch_frames(
        raw_sequences: List[List[List[float]]],
        min_dist: int = MIN_DIST,
        min_sequence_len: int = MIN_SEQUENCE_LEN) -> List[List[List[float]]]:
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
    :param min_dist: minimum distance between centroids for same sequence
    :type  min_dist: int
    :param min_sequence_len: minimum number of frames per sequence
    :type  min_sequence_len: int

    :returns new_sequences: the processed sequences
    :type    new_sequences: List[List[List[float]]]
    """
    new_sequences = []

    for raw_sequence in raw_sequences:
        new_sequence = []

        # Keep track of centroid from last frame
        last_frame_centroid = None
        # If less than MAX_DROPPED_FRAMES are dropped,
        # the sequences will be stitched together.
        num_dropped_frames = 0

        for frame_i, frame in enumerate(raw_sequence):
            # Create new sequence if the maximum amount
            # of dropped frames was reached.
            if len(frame) < 2:
                # Label or OpenPose data is missing
                continue
            elif not last_frame_centroid:
                log.debug(f"Appending first frame.")
                # this frame is the first in the sequence
                new_sequence.append(frame)
                last_frame_centroid = _centroid(frame)

            elif num_dropped_frames >= MAX_DROPPED_FRAMES:
                log.debug(f"Max dropped frames reached, creating new sequence.")
                if len(new_sequence) > min_sequence_len:
                    new_sequences.append(new_sequence)
                num_dropped_frames = 0
                new_sequence = []

            else:
                current_centroid = _centroid(frame)
                if _dist(current_centroid, last_frame_centroid) < min_dist \
                        and int(frame[0]) != 0:
                    # Current and previous frames are likely of the
                    # same participant. frame[0] == 0 equal to the label
                    # indicating there is "no participant".
                    new_sequence.append(frame)
                else:
                    # log.debug("Frame distance too great, dropping.")
                    # This is a dud. Don't use it. It either has
                    # no participant (label = 0), or contains a different
                    # person than the wanted participant.
                    num_dropped_frames += 1

                # Update position of last frame to current frame
                last_frame_centroid = current_centroid

        if len(new_sequence) >= min_sequence_len:
            new_sequences.append(new_sequence)

    return new_sequences


def normalize(
        raw_sequences: List[List[List[float]]]) -> List[List[List[float]]]:
    """
    Applies zero mean and unit variance to all positions
    within a frame.
    """
    for s_index, sequence in enumerate(raw_sequences):
        for f_index, frame in enumerate(sequence):
            preprocessed = preprocessing.scale(np.array(frame[1:]))
            sequence[f_index][1:] = preprocessed
            log.debug(sequence[f_index])

    return raw_sequences
