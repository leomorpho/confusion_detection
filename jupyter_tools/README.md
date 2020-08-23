# Jupyter Tools

This directory contains tools developed specifically for our notebook.

## Tools

* `stitch_frames`: removes faulty frames
  * Remove frames containing OpenPose annotations of people other than the main test subject. They can be detected by comparing the centroid of the points of the previous and current frame. Over a certain threshold, we can assume that different people were detected.
* `normalize`: Applies zero mean and unit variance to all positions
  within a frame.

## Tests

Test coverage: 79%

To run the tests, `cd` into the `jupyter_tools` directory and run:

```
❯ pytest 
```

