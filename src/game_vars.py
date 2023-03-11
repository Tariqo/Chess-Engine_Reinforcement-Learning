import os

#player colors:
white = 'white'
black = 'black'

#color schemes
blk = "#769656"
wht = "#eeeed2"

blk = "#6b95bb"
wht = "#c9dcff"


# sprite locations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'img')

# Screen dimensions
WIDTH = 800
HEIGHT = 800

# Board dimensions
ROWS = 8
COLS = 8
TSIZE = WIDTH // COLS