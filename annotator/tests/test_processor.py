import pytest
import logging
import os
from src.infra.processor import FrameProcessor

log = logging.getLogger()
log.setLevel(logging.DEBUG)

TESTDATA = "testdata"

def test_frame_processor_creation():
    frame_processor = FrameProcessor(f"{TESTDATA}/singledir")
    assert(frame_processor.queue == [])
    assert(frame_processor.curr_dir == 'testdata/singledir/raw/2019-10-29-14-21-35.bag')

# class InputOutputCase():
#     """Represents a test case with input_val and expected expected_output"""
#
#     def __init__(self, name, A, B):
#         self.name = name
#         self.A = A
#         self.B = B
#
#
#
# # 3 layers of vectors for Y, Cb, Cr
# full_image_test_cases = [
#     InputOutputCase(
#         name="Nominal",
#         A=[
#             [  # Layer 1
#                 [[123, 123], [123, 123]],
#             ],
#             [  # Layer 2
#                 [[123, 123], [123, 123]],
#             ],
#             [  # Layer 3
#                 [[123, 123], [123, 123]],
#             ]
#         ],
#         B=[123, 123, 123, 123, 123, 123, 123, 123, 123, 123, 123, 123]
#     )
# ]
#
#
# @pytest.mark.parametrize("case", full_image_test_cases)
# def test_layers_to_vector(case):
#     log.info("Case: " + case.name)
#     log.debug("Input: " + str(case.A))
#
#     im = IMGFile()
#     result = im.layers_to_vector(case.A)
#
#     log.debug("Result: " + str(result))
#     assert(result == case.B)
