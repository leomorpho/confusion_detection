# Getting started

## Install required packages
`pip install -r requirements.txt`

Install `ffmpeg`:
* MacOS: `brew install ffmpeg`
* Ubuntu/Debian: `sudo apt install ffmpeg`



### Jupyter Notebook

Find our jupyter notebook [here](https://colab.research.google.com/drive/1GB-D6D5eOkK_TgdmVJ8mqMvPmIvMl7aG?usp=sharing)

## General Design

### Trained Models

The following is a list of trained models that we are considering to extract features from our images/videos.

[**Top 57 Pose Estimation Trained Models**](https://awesomeopensource.com/projects/human-pose-estimation)

Seems like OpenPose and AlphaPose are the best models to detect human pose.

* [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose)
* [AlphaPose](https://github.com/MVIG-SJTU/AlphaPose)

AlphaPose seems to have slightly better performances than OpenPose, but only works on linux or windows. Since both member of the team only have Macos, OpenPose seems a better option.

See [how to install OpenPose on Macos](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation.md)

Because OpenPose can only extract 2D representations of images, we will use the same camera for all the data. 

TODO: number of frames processed by OpenPose

### Work Logs

#### Done

* Installed OpenPose on my laptop (MacOS) and a more powerful desktop (Windows)
* Created a script to run OpenPose on all dataset
  * Extract all frames for every video
  * Run OpenPose on every frame. Due to my limited hardware, I used a hack to get OpenPose to work on folders containing 400+ images. I temporarily copy each image to a `tmp` folder, run OpenPose on that folder, and copy the results back to the new dataset.
* OpenPose is painfully slow. It originally took 20s per frame on my laptop and 12s per frame on my desktop. I figured out how to change the model used. For CPU only, the `COCO` model is fastest. This change improved my latop to 11s per frame and my desktop to about 10s per frame (curiously no big difference there).

#### Todo

* The annotation tool currently
* Because both the `COCO` and `BODY_25` models were used to create the dataset with OpenPose, the `json` files will have 2 different numbers of datapoints. Some will have 25 for the`BODY_25` model, others will have 18 (I believe?) for the `COCO` model. Furthermore, there is one `json` created per frame. For a folder of frames (= 1 video), the OpenFace features in the `json` files must be stitched together. The annotation (confused/unknown/not confused/no person) must be added to the stiched object. The resulting `json`, which comprises the OpenFace features and confusion labels must be saved to disk.
* What kind of data augmentation techniques can we use?

### Annotation

We had several problems during annotation:

* OpenFace was set in the single person mode and sometimes would pick up either a research assistant in the background or the Pepper robot. OpenFace tended to also have more difficulty with people of smaller stature, often wrongly selecting the Pepper robot over the human participant. This resulted in some annotation sequences being cut. We will have to deal with this in preprocessing. Solutions are to either

  * Stitch 2 sequences if the number of non-annotated frames between them are low and we are sure that it is the same person
  * Drop the sequence otherwise

* All frames with people had at least 1 person in the frame covered in the characteristic lines of OpenPose. The frames were aggressively compressed to 10% quality to save space.

  ![Screen Shot 2020-08-07 at 11.29.38 AM](README.assets/Screen%20Shot%202020-08-07%20at%2011.29.38%20AM.png)

* When participants were talking to the Pepper robot, the frames were labeled as "confused" if they appeared to annotators to be confused. In a real world scenario, a person talking to another can be confused. A robot designed to assist confused people would realistically not approach two people if one of them is confused, as it should be able to assume that one is helping the other. An interesting case could be of two confused people talking to one another. This may be a valid case for a helper robot to approach them. However, in our current experiment, OpenFace detects a single person in the frame, and we can therefore assume that that is the only person in the room.

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
