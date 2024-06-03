import numpy as np


def format_data(data: np.ndarray) -> np.ndarray:
    """
    :param data: A 3D numpy array where each element is an uint8
    :return: A 3D boolean numpy array
    """

    return data.astype(bool)
