import numpy as np

from . import meta


def format_data(data: np.ndarray, scale: meta.Scale) -> tuple[np.ndarray, np.ndarray]:
    """
    :param data: A 3D numpy array where each element is an uint8
    :param scale: The voxel scale
    :return: The 3D boolean array, translations applied when cropping
    """

    data = data.astype(bool)

    # crop the data to remove any empty space
    data_coords = np.argwhere(data)

    if data_coords.size == 0:
        return data, np.array([0, 0, 0])

    min_xyz = np.min(data_coords, axis=0)
    max_xyz = np.max(data_coords, axis=0)

    translations = min_xyz * scale.xyz()

    return data[min_xyz[0]:max_xyz[0] + 1, min_xyz[1]:max_xyz[1] + 1, min_xyz[2]:max_xyz[2] + 1], translations
