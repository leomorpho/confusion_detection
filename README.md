# Getting started

## Install required packages
`pip install -r requirements.txt`

## Annotation tool
### Start annotation tool
`python annotator/main.py`

### What it does
1. Extract frames for all images for each directory
2. Display all corresponding frames in UI
3. User can choose key 1 to 5 to label images 
    * 1: Not confused
    * 2: Possibly confused
    * 3: Don't know
    * 4: Likely confused
    * 5: Confused
