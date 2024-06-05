import numpy as np


def geom_center(dist_map: np.array, xy_scale: float, z_scale: float) -> np.ndarray:
    """
    Finds the geometric center of the PSD using a weighted average

    :param dist_map: The distance map
    :param xy_scale: Scale factor for x and y coordinates
    :param z_scale: Scale factor for z coordinates
    :return: A 3-element float array containing the geometric center
    """

    # Normalize the grid values so they add up to 1
    grid_normalized = dist_map - np.min(dist_map)
    grid_normalized = grid_normalized / np.sum(grid_normalized)

    # Create arrays of coordinates
    z, y, x = np.indices(dist_map.shape).astype(float)

    # Account for x, y, and z scales
    x *= xy_scale
    y *= xy_scale
    z *= z_scale

    # Calculate the weighted average of the x and y coordinates
    center_x = np.sum(x * grid_normalized)
    center_y = np.sum(y * grid_normalized)
    center_z = np.sum(z * grid_normalized)

    return np.array([center_x, center_y, center_z])
