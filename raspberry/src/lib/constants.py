from enum import Enum
import numpy as np

# Object detection
MIN_OBJECT_AREA = 500

# Color detection
MIN_COLOR_AREA = 500

# Comunicacion Serial
SERIAL_PORT = "/dev/ttyACM0" #"COM5"
BAUDRATE = 9600

class ROI(Enum):
    FRONT = "front"
    BACK = "back"
    NEXT_TILE_MAZE = "nextTileMaze"


# Cordenadas de ROIs
ROI_COORDINATES = {
    ROI.FRONT: {
        "x1": 0,
        "y1": 0,
        "x2": 100,
        "y2": 100
    },
    ROI.BACK: {
        "x1": 0,
        "y1": 0,
        "x2": 150,
        "y2": 150
    },
    ROI.NEXT_TILE_MAZE: {
        "x1": 0,
        "y1": 0,
        "x2": 200,
        "y2": 200
    }
}

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    ORANGE = "orange"
    PINK = "pink"
    WHITE = "white"

# Color detection - HSV
COLOR_RANGES_HSV = {
    Color.RED: [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([170, 100, 100]), np.array([180, 255, 255]))
    ],

    Color.GREEN: [
        (np.array([33, 87, 59]), np.array([79, 255, 163]))
    ],

    Color.BLUE: [
        (np.array([75, 87, 59]), np.array([122, 255, 163]))
    ],

    Color.ORANGE: [
        (np.array([0, 141, 132]), np.array([15, 255, 255]))
    ],

    Color.YELLOW: [
        (np.array([0, 50, 194]), np.array([49, 255, 255]))
    ],

    Color.PINK: [
        (np.array([0, 50, 194]), np.array([179, 255, 255]))
    ],

    Color.WHITE: [
        (np.array([0, 0, 180]), np.array([180, 60, 255]))
    ],
}

# Color detection - THRESHOLD
THRESHOLD_RANGES = {
    Color.RED: (0, 80),
    Color.GREEN: (0, 80),
    Color.BLUE: (0, 80),
    Color.YELLOW: (0, 80),
    Color.ORANGE: (0, 80),
    Color.PINK: (0, 80),
    Color.WHITE: (180, 255),
}