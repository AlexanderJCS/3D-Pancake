import numpy as np

from . import data
from . import obb
from . import dist
from . import center

import visual


def get_area(raw_data: np.ndarray, xy_len: float, z_len: float, visualize: bool = False, c_s: float = 0.67) -> float:
    """
    Processes the data
    
    :param raw_data: The raw data to find the surface area of
    :param xy_len: The length of a voxel in the x or y direction
    :param z_len: The length of a voxel in the z direction
    :param visualize: Whether to visualize the data
    :param c_s: The constant for the sigma formula
    :return: Finds the surface area given the raw data
    """
    
    # Step A: load and format data
    formatted = data.format_data(raw_data)

    # Step B: oriented bounding boxes
    bounding_box: list[obb.Obb] = obb.get_obbs(formatted, xy_len, z_len, visualize=visualize)

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, xy_len, z_len)
    blurred = dist.blur(distance_map, c_s, xy_len, z_len)

    if visualize:
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    center_point = center.geom_center(blurred, xy_len, z_len)

    if visualize:
        visual.o3d_point_cloud(distance_map, center_point)

    return 0
    