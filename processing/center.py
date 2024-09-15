import numpy as np

from .data import meta


def geom_center(dist_map: np.array, scale: meta.Scale) -> np.ndarray:
    """
    Finds the geometric center of the PSD using the geometric center of the top 1% of the PSD distance map

    :param dist_map: The distance map
    :param scale: The scale of a voxel
    :return: A 3-element float array containing the geometric center in XYZ coordinates
    """

    # Find the top 1% of the PSD
    top_vertices = np.percentile(dist_map, 99)
    top_indices = np.where(dist_map >= top_vertices)
    
    # Compute the center
    center = np.mean(top_indices, axis=1)
    center = center * scale.zyx()

    return center[::-1]
