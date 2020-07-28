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
* The user can go to the next or previous frame. This does not set the frame to any confusion value.
* If the user holds down any of the accepted keys, the images will cycle like a movie.

![Screen Shot 2020-07-17 at 5.15.58 PM](README.assets/Screen%20Shot%202020-07-17%20at%205.15.58%20PM.png)

### Issues
The robot camera has a higher frame rate than the room cameras. This makes the robot frames run too fast compared to the room cameras. We can fix that in processing later.

