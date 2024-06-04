import numpy as np
from scipy import ndimage


def gen_dist_map(data: np.ndarray, xy_scale: float, z_scale: float) -> np.ndarray:
    # add padding around data to prevent edges not counting as 0
    data = np.pad(data, 1, mode="constant")

    dist_map_positives = ndimage.distance_transform_edt(
        data, sampling=[z_scale, xy_scale, xy_scale]
    )

    dist_map_negatives = ndimage.distance_transform_edt(
        ~data, sampling=[z_scale, xy_scale, xy_scale]  # ~data is bitwise NOT, flipping booleans
    )

    # remove padding from the distance maps
    dist_map_positives = dist_map_positives[1:-1, 1:-1, 1:-1]
    dist_map_negatives = dist_map_negatives[1:-1, 1:-1, 1:-1]

    return dist_map_positives + dist_map_negatives
