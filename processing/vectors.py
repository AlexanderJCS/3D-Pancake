import numpy as np

from .data import meta


def gen_gradient(dist_map: np.ndarray, scale: meta.Scale) -> np.ndarray:
    """
    Generates the gradient of the data

    :param dist_map: The data to find the gradient of
    :param scale: The scale of the data
    :return: The gradient of the data
    """

    gradient_z, gradient_y, gradient_x = np.gradient(dist_map, *scale.zyx())
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


def project_points(points: np.array, vec_x: np.array) -> np.array:
    """
    Projects the points (in [[x, y, z], [...], ...] format onto a new coordinate system. Vec represents the
    x direction of the new coordinate system.

    :param points: The points to project onto the vector in [[x, y, z], [...], ...] format
    :param vec_x: The x-direction vector of the new coordinate system in [x, y, z] format
    :return: The projected points in the same format as points
    """

    vec_x = vec_x / np.linalg.norm(vec_x)
    vec_y = np.cross(np.array([0, 0, 1]), vec_x) / np.linalg.norm(np.cross(np.array([0, 0, 1]), vec_x))
    vec_z = np.cross(vec_x, vec_y) / np.linalg.norm(np.cross(vec_x, vec_y))

    return np.stack(
        [
            np.dot(points, vec_x),
            np.dot(points, vec_y),
            np.dot(points, vec_z)
        ],
        axis=-1
    )
