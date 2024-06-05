"""
This script is used to quickly run the processing pipeline on the data, instead of going through the lengthy
process of opening Dragonfly, loading a session, and selecting an ROI. This script is meant to run independently
and is only for development.
"""

import numpy as np
import processing


def run():
    with open("roi.npy", "rb") as f:
        roi = np.load(f)

    print(processing.area.get_area(roi, 5.03, 42.017))


if __name__ == "__main__":
    run()
