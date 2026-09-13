from enum import Enum
import numpy as np

# Object detection
MIN_OBJECT_AREA = 500

# Object detection
MIN_COLOR_AREA = 500

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
        (np.array([35, 60, 60]), np.array([85, 255, 255]))
    ],

    Color.BLUE: [
        (np.array([90, 80, 50]), np.array([130, 255, 255]))
    ],

    Color.ORANGE: [
        (np.array([10, 100, 100]), np.array([20, 255, 255]))
    ],

    Color.YELLOW: [
        (np.array([20, 80, 80]), np.array([35, 255, 255]))
    ],

    Color.PINK: [
        (np.array([140, 50, 50]), np.array([170, 255, 255]))
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