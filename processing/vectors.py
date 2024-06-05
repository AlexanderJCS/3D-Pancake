import numpy as np

from . import data


def gen_gradient(data: np.ndarray, scale: data.Scale) -> np.ndarray:
    """
    Generates the gradient of the data

    :param data: The data to find the gradient of
    :param scale: The scale of the data
    :return: The gradient of the data
    """

    # todo: verify scale.zyx() is the correct order and that all vectors are pointing the right way
    gradient_x, gradient_y, gradient_z = np.gradient(data, scale.zyx())

    # todo: verify that xyz is the correct order
    return np.stack((gradient_x, gradient_y, gradient_z), axis=-1)
