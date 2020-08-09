# Jupyter Tools

This directory contains tools developed specifically for our notebook.

## Tools

* `check_frames`: preprocesses the raw data
  * Remove frames containing OpenPose annotations of people other than the main test subject. They can be detected by comparing the centroid of the points of the previous and current frame. Over a certain threshold, we can assume that different people were detected.



## Tests

To run the tests:

```
pytest
```

