import pytest
import logging
import os
from src.infra.processor import FrameProcessor

log = logging.getLogger()
log.setLevel(logging.DEBUG)

TESTDATA = "testdata"


def test_frame_processor_creation():
    TESTDIR = f"{TESTDATA}/simplecase"
    fp = FrameProcessor(TESTDIR)
    assert(set(fp.queue) == set(['testdata/simplecase/new_raw/C', 'testdata/simplecase/new_raw/A']))
    assert(fp.curr_dir == f'{TESTDIR}/new_raw/B')
    assert(fp.curr_frame == 1)

    # Go all the way to the end of the frames
    assert(fp.next() == "testdata/simplecase/new_raw/B/0001_rendered.jpeg")

    assert(fp.next() == "testdata/simplecase/new_raw/B/0002_rendered.jpeg")

    assert(fp.next() == "testdata/simplecase/new_raw/B/0003_rendered.jpeg")

    assert(fp.next() == "testdata/simplecase/new_raw/B/0004_rendered.jpeg")

    assert(fp.next() == "testdata/simplecase/new_raw/B/0005_rendered.jpeg")

    # next should be idempotent
    assert(fp.next() == None)
    assert(fp.next() == None)
    assert(fp.next() == None)

    # Go back all the way to the birth of Jesus
    assert(fp.prev() == "testdata/simplecase/new_raw/B/0005_rendered.jpeg")

    assert(fp.prev() == "testdata/simplecase/new_raw/B/0004_rendered.jpeg")

    assert(fp.prev() == "testdata/simplecase/new_raw/B/0003_rendered.jpeg")

    assert(fp.prev() == "testdata/simplecase/new_raw/B/0002_rendered.jpeg")

    assert(fp.prev() == "testdata/simplecase/new_raw/B/0001_rendered.jpeg")


    # Should be idempotent
    assert(fp.prev() == None)
    assert(fp.prev() == None)
    assert(fp.prev() == None)

    assert(fp.next() == "testdata/simplecase/new_raw/B/0001_rendered.jpeg")


def test_next_directory():
    TESTDIR = f"{TESTDATA}/simplecase"
    fp = FrameProcessor(TESTDIR)
    assert(fp.curr_dir == "testdata/simplecase/new_raw/B")
    assert(fp.curr_frame == 1)

    fp.next_directory()
    assert(fp.curr_dir == "testdata/simplecase/new_raw/C")
    assert(fp.curr_frame == 1)

    fp.next_directory()
    assert(fp.curr_dir == "testdata/simplecase/new_raw/A")
    assert(fp.curr_frame == 1)

    fp.next_directory()
    assert(fp.curr_dir == None)
    assert(fp.curr_frame == 1)
