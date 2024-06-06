import numpy as np


def format_data(data: np.ndarray) -> np.ndarray:
    """
    :param data: A 3D numpy array where each element is an uint8
    :return: A 3D boolean numpy array
    """

    data = data.astype(bool)
    # TODO: more methodically add padding
    data = np.pad(data, 100, mode="constant")

    return data
