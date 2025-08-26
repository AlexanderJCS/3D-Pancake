import numpy as np


def get_cropped_roi_arr(roi):
    min_indices = roi.getLocalBoundingBoxMin(0)
    min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()], dtype=int)
    max_indices = roi.getLocalBoundingBoxMax(0)
    max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()], dtype=int)

    cropped_roi = roi.getSubset(*min_indices, 0, *max_indices, 0, None, None)
    cropped = cropped_roi.getAsNDArray()

    return cropped


def roi_to_npz(roi, filename):
    """
    Save the ROI data to a .npz file.

    Parameters:
    roi (numpy.ndarray): The ROI data to be saved.
    filename (str): The name of the output .npz file.
    """
    arr = get_cropped_roi_arr(roi)
    locations = np.argwhere(arr)
    np.savez_compressed(filename, arr=locations)