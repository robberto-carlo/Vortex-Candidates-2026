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
    LINE_SECTION_2_TOP = "lineSection2Top"
    LINE_SECTION_2_BOTTOM = "lineSection2Bottom"
    NEXT_TILE_MAZE = "nextTileMaze"
    NEXT_TILE_NIVELES = "nextTileNiveles"
    


# Cordenadas de ROIs
ROI_COORDINATES = {
    ROI.LINE_SECCION_2: {
        "x1": 0,
        "y1": 220,
        "x2": 640,
        "y2": 280
    },
    ROI.ADVANCE_SECTION_2: {
        "x1": 195,
        "y1": 220,
        "x2": 440,
        "y2": 280
    },
    ROI.LINE_SECTION_2_TOP: {
        "x1": 133,
        "y1": 272,
        "x2": 234,
        "y2": 330
    },
    ROI.LINE_SECTION_2_BOTTOM: {
        "x1": 133,
        "y1": 272,
        "x2": 234,
        "y2": 330
    },
    
    ROI.NEXT_TILE_MAZE: {
        "x1": 230,
        "y1": 190,
        "x2": 400,
        "y2": 330
    },
    ROI.NEXT_TILE_NIVELES: {
        "x1": 260,
        "y1": 135,
        "x2": 390,
        "y2": 220
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
        (np.array([0, 129, 80]), np.array([7, 222, 231]))

        #(np.array([144, 68, 41]), np.array([179, 181, 88])),
        #(np.array([0, 61, 46]), np.array([30, 175, 89]))
    ],

    Color.GREEN: [
        (np.array([42, 50, 54]), np.array([79, 118, 149]))
    ],

    Color.BLUE: [
        (np.array([93, 75, 114]), np.array([115, 193, 213]))
    ],

    Color.ORANGE: [
        (np.array([4, 117, 114]), np.array([13, 196, 223]))
    ],

    Color.YELLOW: [
        (np.array([14, 72, 93]), np.array([25, 175, 211]))
    ],

    Color.PINK: [
        (np.array([165, 100, 130]), np.array([179, 166, 234]))
    ],

    Color.WHITE: [
        (np.array([0, 0, 37]), np.array([179, 38, 255]))
    ],
}

ORANGE_BALL = [
    (np.array([0, 90, 150]), np.array([39, 204, 255]))
]

GREEN_PISTA_B = [
    (np.array([31, 42, 130]), np.array([47, 109, 229]))
]

# Color detection - THRESHOLD
COLOR_RANGES_GRAY = {
    Color.RED: (0, 80),
    Color.GREEN: (0, 88),
    Color.BLUE: (0, 80),
    Color.YELLOW: (0, 80),
    Color.ORANGE: (0, 80),
    Color.PINK: (0, 80),
    Color.WHITE: (127, 255),
}
