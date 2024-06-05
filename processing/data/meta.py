from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Scale:
    """
    A dataclass to store the scale of the data
    :param xy: The length of a voxel in the x or y direction (nanometers)
    :param z: The length of a voxel in the z direction (nanometers)
    """

    xy: float
    z: float

    def __post_init__(self):
        if self.xy <= 0:
            raise ValueError("xy_len must be greater than 0")
        if self.z <= 0:
            raise ValueError("z_len must be greater than 0")

    def xyz(self) -> np.ndarray:
        return np.array([self.xy, self.xy, self.z])

    def zyx(self) -> np.ndarray:
        return np.array([self.z, self.xy, self.xy])