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
    assert(fp.queue == ['testdata/simplecase/raw/2019-10-29-14-21-36.bag'])
    assert(fp.curr_dir == f'{TESTDIR}/raw/2019-10-29-14-21-35.bag')
    assert(fp.curr_frame == 1)

    # Go all the way to the end of the frames
    assert(set(fp.next()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0001.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0001.jpeg'})

    assert(set(fp.next()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0002.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0002.jpeg'})

    assert(set(fp.next()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0003.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0003.jpeg'})

    assert(set(fp.next()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0004.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0004.jpeg'})

    assert(set(fp.next()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0005.jpeg'})

    # next should be idempotent
    assert(fp.next() == [])
    assert(fp.next() == [])
    assert(fp.next() == [])

    # Go back all the way to the birth of Jesus
    assert(set(fp.prev()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0005.jpeg'})

    assert(set(fp.prev()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0004.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0004.jpeg'})

    assert(set(fp.prev()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0003.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0003.jpeg'})

    assert(set(fp.prev()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0002.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0002.jpeg'})

    assert(set(fp.prev()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0001.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0001.jpeg'})

    # Should be idempotent
    assert(fp.prev() == [])
    assert(fp.prev() == [])
    assert(fp.prev() == [])

    assert(set(fp.next()) == {
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/A/0001.jpeg',
        f'{TESTDIR}/raw/2019-10-29-14-21-35.bag/B/0001.jpeg'})


def test_next_directory():
    TESTDIR = f"{TESTDATA}/simplecase"
    fp = FrameProcessor(TESTDIR)
    assert(fp.curr_dir == "testdata/simplecase/raw/2019-10-29-14-21-35.bag")
    assert(fp.curr_frame == 1)

    fp.next_directory(extract_frames=False)
    assert(fp.curr_dir == "testdata/simplecase/raw/2019-10-29-14-21-36.bag")
    assert(fp.curr_frame == 1)

    fp.next_directory(extract_frames=False)
    assert(fp.curr_dir == None)
