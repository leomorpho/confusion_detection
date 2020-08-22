import pytest
import logging
import json
import glob
from typing import List
from jupyter_tools import preprocessing

log = logging.getLogger()
log.setLevel(logging.DEBUG)

TESTDATA = "testdata"


class InputOutputCase():
    """Represents a test case with input_val and expected expected_output"""

    def __init__(self, name, json_path, num_sequences=None):
        self.name = name
        self.json_path = json_path
        self.num_sequences = num_sequences


combined_jsons_cases = [
    InputOutputCase(
        name="Nominal",
        json_path="normal.json",
        num_sequences=4
    ),
    InputOutputCase(
        name="1 frame missing",
        json_path="1_frame_missing.json",
        num_sequences=4
    ),
    InputOutputCase(
        name="2 frame missing",
        json_path="2_frame_missing.json",
        num_sequences=4
    ),
    InputOutputCase(
        name="3 frame missing",
        json_path="3_frame_missing.json",
        num_sequences=8
    ),
    InputOutputCase(
        name="No test subject",
        json_path="no_test_subject.json",
        num_sequences=3
    ),
]


@pytest.mark.parametrize("case", combined_jsons_cases)
def test_stitch_frames(case):
    log.info("Case: " + case.name)
    log.debug("Input: " + str(case.json_path))

    raw_sequences: List[List[List[float]]] = []
    with open(f"{TESTDATA}/{case.json_path}") as f:
        raw_sequences.append(json.loads(f.read()))

    # Add a couple normal sequences to make sure all are
    # returned by preprocessing
    with open(f"{TESTDATA}/normal.json") as f:
        seq = json.loads(f.read())
        raw_sequences.append(seq)
        raw_sequences.append(seq)
        raw_sequences.append(seq)

    processed_sequences = preprocessing.stitch_frames(
        raw_sequences, min_dist=40, min_sequence_len=1)

    len_processed_sequences = len(processed_sequences)
    if len_processed_sequences != case.num_sequences:
        log.error(
            f"Expected {case.num_sequences}, found {len_processed_sequences}")
        log.error(json.dumps(processed_sequences, indent=2))
    assert(len_processed_sequences == case.num_sequences)


def test_only_subjects_in_frames():
    DATA_DIR = "../data/combined_jsons"
    dataset_paths = glob.glob(f"{DATA_DIR}/*")

    raw_sequences = []

    for path in dataset_paths:
        with open(path, "r") as f:
            sequences = json.loads(f.read())
        raw_sequences.append(sequences)

    assert(len(raw_sequences) == len(dataset_paths) )

    parsed_sequences = preprocessing.stitch_frames(
        raw_sequences, min_dist=40, min_sequence_len=10)

    assert(len(parsed_sequences) > len(dataset_paths) )

    for sequence in parsed_sequences:
        for frame in sequence:
            assert(int(frame[0]) in {1, 2, 3})
