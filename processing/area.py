import numpy as np

from . import data
from . import obb
from . import dist
import visual


def get_area(raw_data: np.ndarray, xy_len: float, z_len: float) -> float:
    """
    Processes the data
    
    :param raw_data: The raw data to find the surface area of
    :param xy_len: The length of a voxel in the x or y direction
    :param z_len: The length of a voxel in the z direction
    :return: Finds the surface area given the raw data
    """
    
    # Step A: load and format data
    formatted = data.format_data(raw_data)

    # Step B: oriented bounding boxes
    bounding_box: list[obb.Obb] = obb.get_obbs(formatted, xy_len, z_len)

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, xy_len, z_len)

    visualizer = visual.Interactive3DVisualizer(distance_map)
    visualizer.visualize()

    return 0
    