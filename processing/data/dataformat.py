from typing import Optional

from skimage import measure
import numpy as np

from . import meta


def format_data(data: np.ndarray, downsample: bool, scale: Optional[meta.Scale]) -> np.ndarray:
    """
    :param data: A 3D numpy array where each element is an uint8
    :param downsample: Whether to downsample the data
    :param scale The scale of the image. Can be None if downsample = False
    :return: A 3D boolean numpy array
    """

    data = data.astype(bool)
    # TODO: add padding in a better way
    data = np.pad(data, 30, mode="constant")
    
    if downsample:
        scale_factor_xy = int(round(scale.z / scale.xy))
        scale_factor_z = 1
        data = measure.block_reduce(data, (scale_factor_z, scale_factor_xy, scale_factor_xy), np.max)

    return data
