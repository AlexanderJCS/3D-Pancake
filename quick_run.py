"""
This script is used to quickly run the processing pipeline on the data, instead of going through the lengthy
process of opening Dragonfly, loading a session, and selecting an ROI. This script is meant to run independently
and is only for development.
"""

import numpy as np
from processing import processing
from processing import data


def run():
    with open("data/min_extent_z.npy", "rb") as f:
        roi = np.load(f)

    print(processing.get_area(roi, data.Scale(5.03, 42.017), visualize=True))


if __name__ == "__main__":
    run()
