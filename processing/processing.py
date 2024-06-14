from dataclasses import dataclass

import numpy as np

from . import data
from . import bounding_box
from . import dist
from . import center
from . import mesh
from . import vectors

import visual


@dataclass(frozen=True)
class PancakeOutput:
    """
    Dataclass to hold the output of the pancake processing pipeline
    """
    area_nm: float
    center: np.ndarray
    obb: bounding_box.Obb
    points: np.ndarray
    psd_mesh: mesh.Mesh
    gradient: np.ndarray
    projected_gradient: np.ndarray


def get_area(
        raw_data: np.ndarray, scale: data.Scale, visualize: bool = False, c_s: float = 0.67, downsample: bool = False,
        visualize_end: bool = False
) -> PancakeOutput:
    """
    Processes the data
    
    :param raw_data: The raw data to find the surface area of
    :param scale: The scale bar
    :param visualize: Whether to visualize the data
    :param c_s: The constant for the sigma formula
    :param downsample: Whether to downsample the data to the z axis scale
    :return: A PancakeOutput class, containing surface area and a bunch of other data
    """

    # Step A: load and format data
    formatted = data.format_data(raw_data, downsample, scale)
    
    if downsample:
        scale = data.Scale(scale.z, scale.z)

    # Step B: oriented bounding boxes
    obb = bounding_box.Obb(formatted, scale)

    if visualize:
        visual.vis_3d(
            formatted, scale, "Step B: OBB",
            obb=obb,
            vector=[obb.o3d_obb.center, obb.get_rotation_vec()]
        )

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, scale, downsample)
    blurred = dist.blur(distance_map, c_s, scale)

    if visualize:
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    # Step D: find the center
    center_point = center.geom_center(distance_map, scale)

    # Step E: create the mesh
    psd_mesh = mesh.Mesh(obb, center_point, scale)

    if visualize:
        visual.vis_3d(
            distance_map, scale, "Step E: Mesh",
            center=center_point,
            obb=obb,
            psd_mesh=psd_mesh,
            show_dist_map=True
        )

    # Step F: calculate gradient
    gradient = vectors.gen_gradient(blurred, scale)

    if visualize:
        visual.vis_3d(
            distance_map, scale, "Step F: Gradient",
            center=center_point,
            obb=obb,
            psd_mesh=psd_mesh,
            vectors=gradient
        )

    # Step G: project gradient onto normal
    normal = obb.get_normal()
    projected_gradient = vectors.project_on_normal(gradient, normal)

    if visualize:
        visual.vis_3d(
            distance_map, scale, "Step G: Projected Gradient",
            center=center_point,
            obb=obb,
            psd_mesh=psd_mesh,
            vector=[obb.o3d_obb.center, normal],
            vectors=projected_gradient
        )

    # Step H: deform the mesh
    while psd_mesh.error() > 0.1:
        psd_mesh.deform(projected_gradient, scale)

    if visualize or visualize_end:
        visual.vis_3d(
            distance_map, scale, "Step H: Deformed Mesh",
            center=center_point,
            obb=obb,
            psd_mesh=psd_mesh
        )

    # Step I: move the vertices into the nearest OBB
    psd_mesh.clip_vertices(formatted, scale)

    if visualize or visualize_end:
        visual.vis_3d(
            distance_map, scale, "Step I: Clipped Vertices",
            center=center_point,
            obb=obb,
            psd_mesh=psd_mesh
        )

    return PancakeOutput(
        psd_mesh.area(),
        center_point,
        obb,
        np.argwhere(formatted)[:, ::-1] * scale.xyz(),
        psd_mesh,
        gradient,
        projected_gradient
    )
    