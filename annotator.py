import glob

from ipywidgets import Label, HTML, HBox, Image, VBox, Box, HBox
from ipyevents import Event
from IPython.display import display

DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"


def get_non_processed_data():
    # Make set of already processed files
    processed = glob.glob(f"{DATA_PROCESSED}")

    raw = glob.glob(f"DATA_RAW")


class Annotator:
    def __init__(self):
        l = Label('Click or type on me!')
        l.layout.border = '2px solid red'

        h = HTML('Event info')
        d = Event(source=l, watched_events=['click', 'keydown', 'mouseenter'])

        d.on_dom_event(self.handle_event)

        self.display(l, h)

    def handle_event(self, event):
        lines = ['{}: {}'.format(k, v) for k, v in event.items()]
        content = '<br>'.join(lines)
        h.value = content

    # Select a folder
    # Extract frames for all videos in that folder
    # Show one frame for all 3-4 videos and let user label. If some images are missing, don't fail.
        # Only stop when all videos have no more images
    # Write the results as a json to the processed folder. Extract the images to processed if they are missing. Only commit json/csvs.
