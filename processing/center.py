import numpy as np

from . import data


def geom_center(dist_map: np.array, scale: data.Scale) -> np.ndarray:
    """
    Finds the geometric center of the PSD using a weighted average

    :param dist_map: The distance map
    :param scale: The scale of a voxel
    :return: A 3-element float array containing the geometric center
    """

    # Normalize the grid values so they add up to 1
    grid_normalized = dist_map - np.min(dist_map)
    grid_normalized = grid_normalized / np.sum(grid_normalized)

    # Create arrays of coordinates
    z, y, x = np.indices(dist_map.shape).astype(float)

    # Account for x, y, and z scales
    x *= scale.xy
    y *= scale.xy
    z *= scale.z

    # Calculate the weighted average of the x and y coordinates
    center_x = np.sum(x * grid_normalized)
    center_y = np.sum(y * grid_normalized)
    center_z = np.sum(z * grid_normalized)

    return np.array([center_x, center_y, center_z])
