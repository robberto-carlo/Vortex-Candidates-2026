from enum import Enum
import numpy as np

# Object detection
MIN_OBJECT_AREA = 500

# Color detection
MIN_COLOR_AREA = 500

# Comunicacion Serial
SERIAL_PORT = "/dev/ttyUSB0" #"COM5"
BAUDRATE = 9600

class ROI(Enum):
    LINE_SECCION_2 = "lineSeccion2"
    ADVANCE_SECTION_2 = "AdvanceSeccion2"
    NEXT_TILE_MAZE = "nextTileMaze"
    NEXT_TILE_NIVELES = "nextTileNiveles"


# Cordenadas de ROIs
ROI_COORDINATES = {
    ROI.LINE_SECCION_2: {
        "x1": 0,
        "y1": 0,
        "x2": 150,
        "y2": 150
    },
    ROI.ADVANCE_SECTION_2: {
        "x1": 0,
        "y1": 0,
        "x2": 150,
        "y2": 150
    },
    ROI.NEXT_TILE_MAZE: {
        "x1": 130,
        "y1": 290,
        "x2": 510,
        "y2": 480
    },
    ROI.NEXT_TILE_NIVELES: {
        "x1": 0,
        "y1": 250,
        "x2": 640,
        "y2": 480
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
        #(np.array([0, 100, 100]), np.array([10, 255, 255])),
        #(np.array([170, 100, 100]), np.array([180, 255, 255]))
        (np.array([138, 49, 60]), np.array([179, 197, 255]))
    ],

    Color.GREEN: [
        (np.array([61, 123, 81]), np.array([86, 255, 255]))
    ],

    Color.BLUE: [
        (np.array([91, 140, 82]), np.array([127, 255, 255]))
    ],

    Color.ORANGE: [
        (np.array([0, 141, 132]), np.array([15, 255, 255]))
    ],

    Color.YELLOW: [
        (np.array([0, 0, 126]), np.array([83, 131, 208]))
    ],

    Color.PINK: [
        (np.array([128, 55, 154]), np.array([158, 168, 255]))
    ],

    Color.WHITE: [
        (np.array([89, 0, 153]), np.array([138, 49, 224]))
    ],
}

ORANGE_BALL = [
    (np.array([0, 141, 132]), np.array([15, 255, 255]))
]

# Color detection - THRESHOLD
THRESHOLD_RANGES = {
    Color.RED: (0, 80),
    Color.GREEN: (0, 88),
    Color.BLUE: (0, 80),
    Color.YELLOW: (0, 80),
    Color.ORANGE: (0, 80),
    Color.PINK: (0, 80),
    Color.WHITE: (127, 255),
}