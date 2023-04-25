import os

#player colors:
white = 'white'
black = 'black'

#color schemes
# blk = "#769656"
wht = "#dbdcea"

blk = "#3a414c"
# wht = "#9b9ea1"


# sprite locations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'img')

# Screen dimensions
W_WIDTH = 1000
WIDTH = 800
HEIGHT = 800

# Board dimensions
ROWS = 8
COLS = 8
TSIZE = WIDTH // COLS