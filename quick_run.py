"""
This script is used to quickly run the processing pipeline on the data, instead of going through the lengthy
process of opening Dragonfly, loading a session, and selecting an ROI. This script is meant to run independently
and is only for development.
"""

import numpy as np
import processing
# import matplotlib.pyplot as plt


def run():
    with open("roi.npy", "rb") as f:
        roi = np.load(f)

    # plot boolean voxel data with matplotlib
    # ax = plt.figure().add_subplot(projection='3d')
    # ax.voxels(roi, facecolor="red", edgecolor='k')
    #
    # plt.show()


if __name__ == "__main__":
    run()
