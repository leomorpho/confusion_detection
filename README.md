# Getting started

## Install required packages
`pip install -r requirements.txt`

Install `ffmpeg`:
* MacOS: `brew install ffmpeg`
* Ubuntu/Debian: `sudo apt install ffmpeg`

## Annotation tool
You will need the `data` directory to have the `raw` directory filled with the video data.
```
- data
    - raw
        - 2019-12-10-15-19-34.bag
        - 2019-12-10-15-19-32.bag
        - 2019-12-10-15-05-30.bag
    - processed
```

### Start annotation tool

Due to Python's weird import path, the app must be run from within the `annotator` package (see below).

`cd annotator`
`python3 main.py`

Note that frames get extracted one video at a time. Aka, if you are labeling a directory containing videos in it, only these videos will be extracted. I wanted to extract one in advance in the background (on a different thread) but it's too complicated and would require too much time from me. I added an option in the File menu to extract all frames from all directories. I recommend you do that first. It will take forever, the app will probably hang (and unfortunately giving you no feedback...), but look in the terminal and you will see it's doing stuff. The advantage is you won't have to wait later when cycling across all directories..

### What it does
1. Extract frames for all images for each directory
2. Display all corresponding frames in UI

* User can choose key 1 to 5 to label images.
    * 1: Not confused
    * 2: Possibly confused
    * 3: Don't know
    * 4: Likely confused
    * 5: Confused
* The user can go to the next or previous frame by pressing the left and right arrows. These keys do not set the frame to any confusion value.
* If the user holds down any of the accepted keys, the images will cycle like a movie.
* There may be more or less than 4 cameras. However, only 4 can be shown in this implementation. The upper left corner of the app window shows the number of cameras shown at every frame.
* Data is saved at every frame change.

![Screen Shot 2020-07-28 at 7.13.54 PM](README.assets/Screen%20Shot%202020-07-28%20at%207.13.54%20PM.png)

### Issues

The robot camera has a higher frame rate than the room cameras. This makes the robot frames run too fast compared to the room cameras. We can fix that in processing later.

### Development

#### Tests

##### Dummy test data

To run the user interface with dummy test data, simply run the `main.py` with any extra arguments. The following is an example:

```
python main.py 1
```



##### Pytest

From within the `annotator` package, you can run the following commands:

```bash
# Run whole test suite
pytest

# See test coverage
pytest --cov=src tests/
```

