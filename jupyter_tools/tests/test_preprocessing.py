import pytest
import logging
import json
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
        num_sequences=1
    ),
    InputOutputCase(
        name="1 frame missing",
        json_path="1_frame_missing.json",
        num_sequences=1
    ),
    InputOutputCase(
        name="2 frame missing",
        json_path="2_frame_missing.json",
        num_sequences=1
    ),
    InputOutputCase(
        name="3 frame missing",
        json_path="3_frame_missing.json",
        num_sequences=2
    ),
]


@pytest.mark.parametrize("case", combined_jsons_cases)
def test_check_frames(case):
    log.info("Case: " + case.name)
    log.debug("Input: " + str(case.json_path))

    raw_sequences: List[List[List[float]]] = []
    with open(f"{TESTDATA}/{case.json_path}") as f:
        raw_sequences.append(json.loads(f.read()))

    processed_sequences = preprocessing.check_frames(raw_sequences)
    log.debug(processed_sequences)

    assert(len(processed_sequences) == case.num_sequences)
