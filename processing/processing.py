import functools
from dataclasses import dataclass
from typing import Optional

import numpy as np

from . import data
from . import bounding_box
from . import dist
from . import center
from . import mesh
from . import vectors

# Workaround since running Dragonfly with OrsMinimalStartupScript.py causes the package path to be different
if __package__.count(".") == 0:
    import visual
else:
    from .. import visual


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

    """
    The translations made to the OBB and mesh when padding the data. Used to translate the vertices back to the original
    when creating the output mesh to visualize in Dragonfly.
    """
    translations: np.ndarray

    def area_microns(self) -> float:
        """
        Gets the area in um^2

        :return: The area in um^2
        """

        return self.area_nm / 1e6


def get_area(
        raw_data: np.ndarray, scale: data.Scale, visualize: bool = False, c_s: float = 0.67,
        visualize_end: bool = False, visualize_unclipped: bool = False,
        dist_threshold: Optional[float] = None, visualize_signal=None
) -> PancakeOutput:
    """
    Processes the data
    
    :param raw_data: The raw data to find the surface area of
    :param scale: The scale bar
    :param visualize: Whether to visualize the data
    :param c_s: The constant for the sigma formula
    :param visualize_unclipped: Whether to visualize the second to last step
    :param visualize_end: Whether to visualize the final result
    :param dist_threshold: The distance threshold to clip each vertex in the final step. If None, the threshold is
                           equal to max(scale.xy, scale.z)
    :param visualize_signal: The signal to emit the visualization to. Used for PyQt
    :return: A PancakeOutput class, containing surface area and a bunch of other data
    """

    # TODO: code cleanup - this function is very long and can be shortened easily through extraction

    # Step A: load and format data
    formatted = data.format_data(raw_data)

    # Step B: oriented bounding boxes
    obb = bounding_box.Obb(formatted, scale)

    # Step Ba: Expand the dataset so the OBB does not have values outside the dataset
    formatted, translations = obb.expand_data(scale, formatted)

    if visualize:
        if visualize_signal:
            visualize_signal.emit(functools.partial(
                visual.vis_3d,
                formatted, scale, "Step A: Formatted Data",
                obb=obb
            ))
        else:
            visual.vis_3d(
                formatted, scale, "Step B: OBB",
                obb=obb
            )

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, scale)
    blurred = dist.blur(distance_map, c_s, scale)

    if visualize and not visualize_signal:
        # don't show in the signal since matplotlib doesn't play well with PyQt
        
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    # Step D: find the center
    center_point = center.geom_center(distance_map, scale)

    # Step E: create the mesh
    psd_mesh = mesh.Mesh(obb, center_point, scale)

    if visualize:
        if visualize_signal:
            visualize_signal.emit(functools.partial(
                visual.vis_3d,
                distance_map, scale, "Step E: Mesh",
                center=center_point,
                obb=obb,
                psd_mesh=psd_mesh
            ))
        else:
            visual.vis_3d(
                distance_map, scale, "Step E: Mesh",
                center=center_point,
                obb=obb,
                psd_mesh=psd_mesh
            )

    # Step F: calculate gradient
    gradient = vectors.gen_gradient(blurred, scale)

    if visualize:
        if visualize_signal:
            visualize_signal.emit(functools.partial(
                visual.vis_3d,
                distance_map, scale, "Step F: Gradient",
                center=center_point,
                obb=obb,
                psd_mesh=psd_mesh,
                vectors=gradient
            ))
        else:
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
        if visualize_signal:
            visualize_signal.emit(functools.partial(
                visual.vis_3d,
                distance_map, scale, "Step G: Projected Gradient",
                center=center_point,
                obb=obb,
                psd_mesh=psd_mesh,
                vector=[obb.o3d_obb.center, normal],
                vectors=projected_gradient
            ))
        else:
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

    if visualize or visualize_unclipped:
        if visualize_signal:
            visualize_signal.emit(functools.partial(
                visual.vis_3d,
                distance_map, scale, "Step H: Deformed Mesh",
                center=center_point,
                obb=obb,
                psd_mesh=psd_mesh,
                vectors=projected_gradient
            ))
        else:
            visual.vis_3d(
                distance_map, scale, "Step H: Deformed Mesh",
                center=center_point,
                obb=obb,
                psd_mesh=psd_mesh,
                vectors=projected_gradient
            )

    # Step I: move the vertices into the nearest OBB
    psd_mesh.clip_vertices(formatted, scale, dist_threshold)

    if visualize or visualize_end:
        if visualize_signal:
            visualize_signal.emit(functools.partial(
                visual.vis_3d,
                distance_map, scale, "Step I: Clipped Vertices",
                obb=obb,
                psd_mesh=psd_mesh
            ))
        else:
            visual.vis_3d(
                distance_map, scale, "Step I: Clipped Vertices",
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
        projected_gradient,
        translations
    )
    