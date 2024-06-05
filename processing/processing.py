import numpy as np

from . import data
from . import obb
from . import dist
from . import center

import visual


def get_area(raw_data: np.ndarray, scale: data.Scale, visualize: bool = False, c_s: float = 0.67) -> float:
    """
    Processes the data
    
    :param raw_data: The raw data to find the surface area of
    :param scale: The scale bar
    :param visualize: Whether to visualize the data
    :param c_s: The constant for the sigma formula
    :return: Finds the surface area given the raw data
    """
    
    # Step A: load and format data
    formatted = data.format_data(raw_data)

    # Step B: oriented bounding boxes
    bounding_box: list[obb.Obb] = obb.get_obbs(formatted, scale, visualize=visualize)

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, scale)
    blurred = dist.blur(distance_map, c_s, scale)

    if visualize:
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    center_point = center.geom_center(distance_map, xy_len, z_len)

    if visualize:
        visual.o3d_point_cloud(distance_map, center_point, xy_len, z_len)

    return 0
    