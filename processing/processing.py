import numpy as np

from . import data
from . import obb
from . import dist
from . import center
from . import mesh

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
    main_obb, blob_obbs = obb.get_obbs(formatted, scale)

    if visualize:
        visual.o3d_point_cloud(raw_data, scale, obbs=[main_obb] + blob_obbs)

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, scale)
    blurred = dist.blur(distance_map, c_s, scale)

    if visualize:
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    # Step D: find the center
    center_point = center.geom_center(distance_map, scale)

    if visualize:
        visual.o3d_point_cloud(distance_map, scale, center=center_point)

    # Step E: create the mesh
    psd_mesh = mesh.Mesh(main_obb, center_point)

    return 0
    