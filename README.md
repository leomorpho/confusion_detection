# Getting started

## Install required packages
`pip install -r requirements.txt`

## Annotation tool
You will need the `data` directory to have the `raw` directory filled with the video data.
```
- data
    - raw
        - raw_original/2019-12-10-15-19-34.bag
        - data/raw_original/2019-12-10-15-05-30.bag
    - processed
```

### Start annotation tool
`python annotator/main.py`

### What it does
1. Extract frames for all images for each directory
2. Display all corresponding frames in UI

* User can choose key 1 to 5 to label images.
    * 1: Not confused
    * 2: Possibly confused
    * 3: Don't know
    * 4: Likely confused
    * 5: Confused
* Can go to previous or next frame. If next frame has not been labeled yet, it will be labeled as "ambivalent".

### Issues
The room cameras and the robot camera have different frame rates, with the robot camera having a higher frame rate.
