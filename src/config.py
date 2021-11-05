from keras.optimizers import Adam

# General image options
IMAGE_SIZE = (128, 128)  # input images are scaled to this resolution
COLOR_TYPE = 'rgb'  # change to grayscale if your images are monochrome
CHANNELS = 1 if COLOR_TYPE == 'grayscale' else 3

# Main class dictionary - this needs to match folder names in your training dataset
CLASS_DICT = {
    "TUM" : 0,
    "NORM": 2,
    "LYM": 3,
    "MUC": 5,
    "ADI": 6,
    "MUS": 7
}

# Default optimizer
DEFAULT_OPTIMIZER = Adam()

# Cliping EPS
EPS = 1e-6
