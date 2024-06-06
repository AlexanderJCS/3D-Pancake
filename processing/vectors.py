import numpy as np

from . import data


def gen_gradient(dist_map: np.ndarray, scale: data.Scale) -> np.ndarray:
    """
    Generates the gradient of the data

    :param dist_map: The data to find the gradient of
    :param scale: The scale of the data
    :return: The gradient of the data
    """

    # todo: verify scale.zyx() is the correct order and that all vectors are pointing the right way
    gradient_z, gradient_y, gradient_x = np.gradient(dist_map, *scale.zyx())

    # todo: verify that xyz is the correct order
    return np.stack((gradient_x, gradient_y, gradient_z), axis=-1)


def project_on_normal(gradient: np.array, normal: np.array) -> np.array:
    """
    Projects the gradient onto the normal vector. This is done by taking the dot product of the gradient and the normal.

    :param gradient: The gradient
    :param normal: The normal vector
    :return: The projected gradient
    """

    magnitudes = np.dot(gradient, normal)
    return normal * magnitudes[:, :, :, np.newaxis]
