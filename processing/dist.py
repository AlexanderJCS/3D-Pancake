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

    return dist_map_positives - dist_map_negatives


def blur(dist_map: np.ndarray, c_s: float, scale_xy: float, scale_z: float) -> np.ndarray:
    # Sigma formula from paper
    sigma = c_s * np.max(dist_map.flatten())

    # if there's any weird problems, try changing the sigma ratio to scale_z / scale_xy or change sigma to
    # sigma_xy, sigma_xy, sigma_z

    # Adjust standard deviations for each axis
    sigma_xy = sigma * (scale_xy / scale_xy)
    sigma_z = sigma * (scale_xy / scale_z)

    # Apply anisotropic Gaussian blur
    return ndimage.gaussian_filter(dist_map, sigma=(sigma_z, sigma_xy, sigma_xy))
