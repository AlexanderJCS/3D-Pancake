import numpy as np
from scipy import ndimage

from .data import meta


def gen_dist_map(data: np.ndarray, scale: meta.Scale) -> np.ndarray:
    # add padding around data to prevent edges not counting as 0
    data = np.pad(data, 1, mode="constant")

    # TODO: instead of a 3D distance map, try using a 2D distance map for each slice
    #  and then combine them to get a 3D distance map

    dist_map_positives = ndimage.distance_transform_edt(
        data, sampling=scale.zyx()
    )

    dist_map_negatives = ndimage.distance_transform_edt(
        ~data, sampling=scale.zyx()  # ~data is bitwise NOT, flipping booleans
    )

    # remove padding from the distance maps
    dist_map_positives = dist_map_positives[1:-1, 1:-1, 1:-1]
    dist_map_negatives = dist_map_negatives[1:-1, 1:-1, 1:-1]

    return dist_map_positives - dist_map_negatives


def blur(dist_map: np.ndarray, c_s: float, scale: meta.Scale) -> np.ndarray:
    # Sigma formula from paper
    sigma = c_s * np.max(dist_map.flatten())

    # if there's any weird problems, try changing the sigma ratio to scale_z / scale_xy or change sigma to
    # sigma_xy, sigma_xy, sigma_z

    # Adjust standard deviations for each axis
    sigma_xy = sigma * (scale.xy / scale.xy)
    sigma_z = sigma * (scale.xy / scale.z)

    # Apply anisotropic Gaussian blur
    return ndimage.gaussian_filter(dist_map, sigma=(sigma_z, sigma_xy, sigma_xy))
