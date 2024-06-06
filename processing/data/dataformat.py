import numpy as np


def format_data(data: np.ndarray) -> np.ndarray:
    """
    :param data: A 3D numpy array where each element is an uint8
    :return: A 3D boolean numpy array
    """

    data = data.astype(bool)
    # TODO: add padding in a better way
    data = np.pad(data, 30, mode="constant")

    return data
