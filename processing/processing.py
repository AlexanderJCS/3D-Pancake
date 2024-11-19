import functools
from dataclasses import dataclass
from typing import Optional

import numpy as np
import open3d as o3d

from . import data
from . import bounding_box
from . import dist
from . import center
from . import mesh
from . import vectors

# Workaround since running Dragonfly with OrsMinimalStartupScript.py causes the package path to be different
if __package__.count(".") == 0:
    import visual
    from log import logger
else:
    from .. import visual
    from ..log import logger


@dataclass(frozen=True)
class PancakeOutput:
    """
    Dataclass to hold the output of the pancake processing pipeline
    """
    area_nm: float
    center: np.ndarray
    obb: bounding_box.Obb
    points: np.ndarray
    psd_mesh: Optional[mesh.Mesh]
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
        logger.debug("Skipping visualization")
        return
        
    if visualize_signal:
        logger.info(f"Visualizing {step_name} via signal")
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
        logger.info(f"Visualizing {step_name} directly")
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
    :return: A PancakeOutput class, containing surface area and a bunch of other data. Returns with zeros/filler data if the input data is empty
    """

    if len(np.argwhere(raw_data)) == 0:
        logger.warning("Data is empty")
        return PancakeOutput(0, np.array([0, 0, 0]), o3d.geometry.OrientedBoundingBox(), np.array([0, 0, 0]), None, np.array([0, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 0]))

    logger.info(f"Starting processing pipeline. Scale: {scale}, c_s: {c_s}, dist_threshold: {dist_threshold}")
    
    # Step A: load and format data
    logger.info("Formatting data")
    formatted, cropping_translations = data.format_data(raw_data, scale)

    # Step B: oriented bounding boxes
    logger.info("Creating OBB")
    obb = bounding_box.Obb(formatted, scale)

    # Step Ba: Expand the dataset so the OBB does not have values outside the dataset
    logger.info("Padding data")
    formatted, padding_translations = obb.expand_data(scale, formatted)

    visualize_step(visualize, visualize_signal, "Step A: Formatted Data", formatted, scale, obb=obb)

    # Step C: distance map
    logger.info("Creating distance map")
    distance_map = dist.gen_dist_map(formatted, scale)
    blurred = dist.blur(distance_map, c_s, scale)
    
    # don't show if it needs to be emitted to a signal since matplotlib doesn't play well with PyQt
    if visualize and not visualize_signal:
        logger.info("Visualizing distance map")
        visualizer = visual.SliceViewer(distance_map)
        visualizer.visualize()

    # Step D: find the center
    logger.info("Finding center")
    center_point = center.geom_center(distance_map, scale)

    # Step E: create the mesh
    logger.info("Creating mesh")
    psd_mesh = mesh.Mesh(obb, center_point, scale)

    visualize_step(visualize, visualize_signal, "Step E: Mesh", distance_map, scale, obb=obb,
                   center_point=center_point, psd_mesh=psd_mesh)

    # Step F: calculate gradient
    logger.info("Calculating gradient")
    gradient = vectors.gen_gradient(blurred, scale)

    visualize_step(visualize, visualize_signal, "Step F: Gradient", distance_map, scale, obb=obb,
                   center_point=center_point, psd_mesh=psd_mesh, vectors_arr=gradient)

    # Step G: project gradient onto normal
    logger.info("Projecting gradient onto normal")
    normal = obb.get_normal()
    projected_gradient = vectors.project_on_normal(gradient, normal)

    visualize_step(visualize, visualize_signal, "Step G: Projected Gradient", distance_map, scale, obb=obb,
                   center_point=center_point, psd_mesh=psd_mesh, vectors_arr=projected_gradient)

    # Step H: deform the mesh
    logger.info("Deforming mesh")
    psd_mesh.bend(projected_gradient, scale)

    visualize_step(visualize or visualize_unclipped, visualize_signal, "Step H: Deformed Mesh", distance_map,
                   scale, obb=obb, center_point=center_point, psd_mesh=psd_mesh, vectors_arr=projected_gradient)

    # Step I: move the vertices into the nearest OBB
    logger.info("Clipping vertices")
    psd_mesh.clip_vertices(distance_map, scale, dist_threshold)

    visualize_step(visualize or visualize_end, visualize_signal, "Step I: Clipped Vertices", distance_map,
                   scale, obb=obb, center_point=center_point, psd_mesh=psd_mesh)

    logger.info("Finished processing pipeline.")

    return PancakeOutput(
        psd_mesh.area(),
        center_point,
        obb,
        np.argwhere(formatted)[:, ::-1] * scale.xyz(),
        psd_mesh,
        gradient,
        projected_gradient,
        cropping_translations + padding_translations
    )
    