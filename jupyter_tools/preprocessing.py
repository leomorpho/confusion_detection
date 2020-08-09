from typing import Tuple, List


MAX_DROPPED_FRAMES = 3
MIN_DISTANCE_BTW_POSITIONS = 1


def centeroidnp(arr):
    """
    Find the centroid for an array of (x, y) points
    """
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length


def dist(pair1: Tuple[float, float], pair2: Tuple[float, float]) -> float:
    """
    Return distance between 2 points as a single scalar
    """
    x_dist = abs(pair1[0] - pair2[0])
    y_dist = abs(pair2[1] - pair2[1])

    return (x_dist + y_dist) / 2


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
            if num_dropped_frames >= MAX_DROPPED_FRAMES:
                new_sequences.append([])
                sequences_count += 1
                new_sequences[sequences_count].append(frame)
            elif not last_frame_centroid:
                # this frame is the first in the sequence
                new_sequences[sequences_count].append(frame)
            else:
                # Create 2D array
                frame = frame[1:]
                frame_positions = list(zip(frame, frame[1:]))[::2]
                current_centroid = centeroidnp(np.array(frame_positions))
                print(current_centroid)
                print(last_frame_centroid)
                if dist(current_centroid, last_frame_centroid) > MIN_DISTANCE_BTW_POSITIONS \
                        and frame[0] != 0:
                    # Current and previous frames are likely of the
                    # same participant.
                    new_sequences[sequences_count].append(frame)
                else:
                    # This is a dud. Don't use it. It either has
                    # no participant (label = 0), or contains a different
                    # person than the wanted participant.
                    num_dropped_frames += 1

                # Update position of last frame to current frame
                last_frame_centroid = current_centroid

    return new_sequences
