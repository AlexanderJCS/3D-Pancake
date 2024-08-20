"""
This script is used to quickly run the processing pipeline on the data, instead of going through the lengthy
process of opening Dragonfly, loading a session, and selecting an ROI. This script is meant to run independently
and is only for development.
"""

import numpy as np
from .processing import processing
from .processing import data


def run():
    with open("data/test/10as065n5.npy", "rb") as f:
        roi = np.load(f)

    # note: c_s = 0.2 provides good results in my experience, but c_s = 0.67 is default
    output = processing.get_area(
        roi,
        data.Scale(5.03, 42.017),
        c_s=0.2,
        visualize=True,
        visualize_unclipped=True,
        visualize_end=True,
        downsample=False,
    )
    
    area_um = output.area_nm / 1e6
    print(f"Area: {area_um:.6f} μm²")


if __name__ == "__main__":
    run()
