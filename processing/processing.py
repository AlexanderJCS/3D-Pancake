import numpy as np

from . import data
from . import obb
from . import dist
from . import center
from . import mesh
from . import vectors

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
        visual.vis_3d(raw_data, scale, obbs=[main_obb] + blob_obbs, vector=[main_obb.o3d_obb.center, main_obb.get_rotation_vec()])

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, scale)
    blurred = dist.blur(distance_map, c_s, scale)

    if visualize:
        visualizer = visual.SliceViewer(blurred)
        visualizer.visualize()

    # Step D: find the center
    center_point = center.geom_center(distance_map, scale)

    if visualize:
        visual.vis_3d(distance_map, scale, center=center_point)

    # Step E: create the mesh
    psd_mesh = mesh.Mesh(main_obb, center_point, scale)

    if visualize:
        visual.vis_3d(distance_map, scale, center=center_point, obbs=[main_obb] + blob_obbs, psd_mesh=psd_mesh)

    # Step F: calculate gradient
    gradient = vectors.gen_gradient(blurred, scale)

    if visualize:
        visual.vis_3d(distance_map, scale, center=center_point, obbs=[main_obb] + blob_obbs, psd_mesh=psd_mesh, vectors=gradient)

    # Step G: project gradient onto normal
    tangent = main_obb.get_rotation_vec()
    normal = np.cross(tangent, np.array([0, 0, 1]))
    projected_gradient = vectors.project_on_normal(gradient, normal)

    if visualize:
        visual.vis_3d(distance_map, scale, center=center_point, obbs=[main_obb] + blob_obbs, psd_mesh=psd_mesh, vector=[main_obb.o3d_obb.center, normal], vectors=projected_gradient)

    # Step H: deform the mesh
    for i in range(100000):
        print(i)
        psd_mesh.deform(projected_gradient, scale)

    if visualize or True:
        visual.vis_3d(distance_map, scale, center=center_point, obbs=[main_obb] + blob_obbs, psd_mesh=psd_mesh)

    return 0
    