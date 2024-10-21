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


def visualize_step(
        visualize: bool, visualize_signal, step_name: str, psd_data: np.ndarray, scale: data.Scale,
        obb=None, center_point=None, psd_mesh=None, vectors_arr=None, vector=None):
    """
    Helper function to handle visualization. Only visualizes if visualize=True
    
    :param visualize: Whether to visualize the step. The function does nothing if False
    :param visualize_signal: The signal to emit the visualization to. Used for PyQt
    :param step_name: The name of the step
    :param psd_data: The data to visualize
    :param scale: The voxel spacing
    :param obb: The oriented bounding box to visualize
    :param center_point: The center of the data
    :param psd_mesh: The mesh to visualize
    :param vectors_arr: The vectors to visualize
    :param vector: The vector to visualize
    
    """
    if not visualize:
        return
        
    if visualize_signal:
        visualize_signal.emit(functools.partial(
            visual.vis_3d,
            psd_data, scale, step_name,
            obb=obb,
            center=center_point,
            psd_mesh=psd_mesh,
            vectors=vectors_arr,
            vector=vector
        ))
    else:
        visual.vis_3d(
            psd_data, scale, step_name,
            obb=obb,
            center=center_point,
            psd_mesh=psd_mesh,
            vectors=vectors_arr,
            vector=vector
        )


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
    
    # Step A: load and format data
    formatted = data.format_data(raw_data)

    # Step B: oriented bounding boxes
    obb = bounding_box.Obb(formatted, scale)

    # Step Ba: Expand the dataset so the OBB does not have values outside the dataset
    formatted, translations = obb.expand_data(scale, formatted)

    visualize_step(visualize, visualize_signal, "Step A: Formatted Data", formatted, scale, obb=obb)

    # Step C: distance map
    distance_map = dist.gen_dist_map(formatted, scale)
    blurred = dist.blur(distance_map, c_s, scale)
    
    # don't show if it needs to be emitted to a signal since matplotlib doesn't play well with PyQt
    if visualize and not visualize_signal:
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    # Step D: find the center
    center_point = center.geom_center(distance_map, scale)

    # Step E: create the mesh
    psd_mesh = mesh.Mesh(obb, center_point, scale)

    visualize_step(visualize, visualize_signal, "Step E: Mesh", distance_map, scale, obb=obb,
                   center_point=center_point, psd_mesh=psd_mesh)

    # Step F: calculate gradient
    gradient = vectors.gen_gradient(blurred, scale)

    visualize_step(visualize, visualize_signal, "Step F: Gradient", distance_map, scale, obb=obb,
                   center_point=center_point, psd_mesh=psd_mesh, vectors_arr=gradient)

    # Step G: project gradient onto normal
    normal = obb.get_normal()
    projected_gradient = vectors.project_on_normal(gradient, normal)

    visualize_step(visualize, visualize_signal, "Step G: Projected Gradient", distance_map, scale, obb=obb,
                   center_point=center_point, psd_mesh=psd_mesh, vectors_arr=projected_gradient)

    # Step H: deform the mesh
    while psd_mesh.error() > 0.1:
        psd_mesh.deform(projected_gradient, scale)

    visualize_step(visualize or visualize_unclipped, visualize_signal, "Step H: Deformed Mesh", distance_map,
                   scale, obb=obb, center_point=center_point, psd_mesh=psd_mesh, vectors_arr=projected_gradient)

    # Step I: move the vertices into the nearest OBB
    psd_mesh.clip_vertices(formatted, scale, dist_threshold)

    visualize_step(visualize or visualize_end, visualize_signal, "Step I: Clipped Vertices", distance_map,
                   scale, obb=obb, center_point=center_point, psd_mesh=psd_mesh)

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
    