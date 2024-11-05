import numpy as np


def format_data(data: np.ndarray) -> np.ndarray:
    """
    :param data: A 3D numpy array where each element is an uint8
    :return: A 3D boolean numpy array
    """

    data = data.astype(bool)

    # crop the data to remove any empty space
    data_coords = np.argwhere(data)

    min_xyz = np.min(data_coords, axis=0)
    max_xyz = np.max(data_coords, axis=0)

    return data[min_xyz[0]:max_xyz[0] + 1, min_xyz[1]:max_xyz[1] + 1, min_xyz[2]:max_xyz[2] + 1]