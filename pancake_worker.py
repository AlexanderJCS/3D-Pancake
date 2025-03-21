import functools
import typing

from PyQt6.QtCore import QThread, pyqtSignal

from . import csv_output
from .processing import data
from typing import Union

from ORSModel import ors

import numpy as np
from .processing import processing
from . import other_algorithms

from .log import logger


def get_cropped_roi_arr(roi: ors.ROI, scale: data.Scale) -> tuple[np.ndarray, np.ndarray]:
    """
    Gets the cropped ROI array. The ROI is cropped to the bounding box of the ROI.

    :param scale: The scale of each voxel
    :param roi: The ROI to crop
    :return: tuple(The cropped ROI array, the transformations required to translate the vertices back to the original
              in world space)
    """
    
    logger.info("Getting cropped ROI array")

    min_indices = roi.getLocalBoundingBoxMin(0)
    min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()], dtype=int)
    max_indices = roi.getLocalBoundingBoxMax(0)
    max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()], dtype=int)

    cropped_roi = roi.getSubset(*min_indices, 0, *max_indices, 0, None, None)
    cropped = cropped_roi.getAsNDArray()
    
    reverse_transformation = (-1 * min_indices * scale.xyz())
    
    logger.debug(f"Cropped to shape {cropped[0].shape} with reverse transformation {reverse_transformation}")
    
    return cropped, reverse_transformation


def mesh_to_ors(mesh: processing.mesh.Mesh, translations: list[np.ndarray], scale: data.Scale) -> ors.Mesh:
    """
    Converts a processing.mesh.Mesh object to a Dragonfly ORS mesh. Used for displaying the final mesh to the user.
    Precondition: The mesh is not none

    :param scale: The voxel spacing
    :param mesh: The mesh to convert
    :param translations: The translations made to the OBB and mesh when padding the data. Used to translate the vertices
        back to the original when creating the output mesh to visualize in Dragonfly.
    :return: The Dragonfly ORS mesh
    """

    logger.info("Converting mesh to ORS mesh")

    o3d_mesh = mesh.mesh

    np_vertices = np.asarray(o3d_mesh.vertices)

    # translate all vertices by 1/2 * scale for the axis to center the mesh at the voxel center
    np_vertices += 0.5 * scale.xyz()

    if translations is not None:
        for translation in translations:
            np_vertices -= translation

    np_vertices = np_vertices.flatten()

    np_triangles = np.asarray(o3d_mesh.triangles).flatten()

    # divide vertices by 1e9 to get meters instead of nanometers
    np_vertices = np_vertices / 1e9

    ors_mesh = ors.FaceVertexMesh()
    ors_mesh.setTSize(1)  # set the time dimension

    # todo: code cleanup - instead of doing this weird for loop thing, flatten np_vertices and np_triangles

    ors_mesh_vertices = ors_mesh.getVertices(0)
    ors_mesh_vertices.setSize(len(np_vertices) * 3)  # multiply by 3 to account for x, y, z

    for i in range(len(np_vertices)):
        ors_mesh_vertices.atPut(i, np_vertices[i])

    ors_triangles = ors_mesh.getEdges(0)
    ors_triangles.setSize(len(np_triangles) * 3)  # multiply by 3 to account for 3 vertices per triangle

    for i in range(len(np_triangles)):
        ors_triangles.atPut(i, np_triangles[i])

    return ors_mesh


def scale_from_roi(roi: ors.ROI) -> data.Scale:
    """
    Gets the scale from the ROI.

    :param roi: The ROI to get the scale from.
    :return: The scale of the ROI.
    """

    return data.Scale(roi.getXSpacing() * 1e9, roi.getZSpacing() * 1e9)


class PancakeWorker(QThread):
    """
    The Pancake Worker class. Allows the surface area to be processed in the background.
    """

    update_output_label = pyqtSignal(str)
    show_visualization = pyqtSignal(functools.partial)

    def __init__(self, selected_roi: Union[None, ors.ROI, ors.MultiROI],
                 visualize_steps: bool, visualize_results: bool, c_s: float,
                 output_filepath: str, compare_lindblad: bool, compare_lewiner: bool, gen_dragonfly_mesh: bool,
                 dist_threshold: typing.Optional[float] = None):
        """
        Initializes the Pancake Worker.

        :param selected_roi: The ROI or MultiROI to process. If none, the worker will not run.
        :param visualize_steps: Whether to visualize each step
        :param visualize_results: Whether to visualize the final result
        :param c_s: The c_s value. How tight a fit the surface is to the data.
        :param output_filepath: The output filepath for the CSV
        :param compare_lindblad: Whether to compare the Lindblad 2005 algorithm in the output CSV
        :param compare_lewiner: Whether to compare the Lewiner 2012 algorithm in the output CSV
        :param gen_dragonfly_mesh: Whether to generate a Dragonfly mesh of the final result and publish it
        :param dist_threshold: The distance threshold to clip each vertex in the final step.
        """

        super().__init__()

        self._selected_roi = selected_roi
        self._visualize_steps = visualize_steps
        self._visualize_results = visualize_results
        self._c_s = c_s
        self._output_filepath = output_filepath
        self._compare_lindblad = compare_lindblad
        self._compare_lewiner = compare_lewiner
        self._gen_dragonfly_mesh = gen_dragonfly_mesh
        self._dist_threshold = dist_threshold

    def _write_to_csv(
            self, names: list[str], outputs: list[float],
            labels: typing.Optional[list[str]] = None,
            lindblad_2005: typing.Optional[list[float]] = None,
            lewiner_2012: typing.Optional[list[float]] = None
    ):
        columns = {}

        if labels is not None:
            columns["Label"] = labels

        columns["Name"] = names
        columns["3D Pancake Area (um²)"] = [str(output) for output in outputs]

        if lindblad_2005 is not None:
            columns["Lindblad 2005 Area / 2 (um²)"] = [str(output) for output in lindblad_2005]
        if lewiner_2012 is not None:
            columns["Lewiner 2012 Area / 2 (um²)"] = [str(output) for output in lewiner_2012]

        try:
            csv_output.write_csv(self._output_filepath, columns)
        except (FileNotFoundError, IsADirectoryError, NotADirectoryError):
            self.update_output_label.emit("Error writing to file. Check the filepath.")
        except PermissionError:
            self.update_output_label.emit("Permission error writing to CSV. Is it open by another program?")

    def process_single_roi(self):
        logger.info("Processing single ROI...")
        
        scale = scale_from_roi(self._selected_roi)
        cropped_roi_arr, original_translations = get_cropped_roi_arr(self._selected_roi, scale)

        output = processing.get_area(
            raw_data=cropped_roi_arr, scale=scale, visualize=self._visualize_steps,
            visualize_end=self._visualize_results, c_s=self._c_s, visualize_signal=self.show_visualization,
            dist_threshold=self._dist_threshold
        )

        # todo: code cleanup: remove duplicate code between single ROI and multi ROI about generating dragonfly mesh
        if self._gen_dragonfly_mesh and output.psd_mesh is not None:
            ors_mesh = mesh_to_ors(output.psd_mesh, [original_translations, output.translations], scale)
            ors_mesh.setTitle(f"3D Pancake Output Mesh: {self._selected_roi.getTitle()}")
            ors_mesh.publish()

        area_output = output.area_microns()

        # todo: code cleanup: remove duplicate code between single ROI and multi ROI about lindblad and lewiner areas
        self.update_output_label.emit("Calculating Lindblad 2005 area...")
        lindblad_2005 = [other_algorithms.surface_area_lindblad_2005(self._selected_roi)] \
            if self._compare_lindblad else None

        self.update_output_label.emit("Calculating Lewiner 2012 area...")
        lewiner_2012 = [other_algorithms.surface_area_lewiner_2012(cropped_roi_arr, scale)] \
            if self._compare_lewiner else None

        self.update_output_label.emit(f"Done. Area: {area_output:.6f} μm²")

        if self._output_filepath == "":
            return

        self._write_to_csv([self._selected_roi.getTitle()], [area_output], lindblad_2005, lewiner_2012)

    def process_multi_roi(self):
        logger.info("Running pancake worker multiroi")
        
        labels = []
        names = []
        outputs = []
        lindblad_2005 = [] if self._compare_lindblad else None
        lewiner_2012 = [] if self._compare_lewiner else None

        for label in range(1, self._selected_roi.getLabelCount() + 1):
            logger.info(f"Processing PSD {label}/{self._selected_roi.getLabelCount()}...")
            
            self.update_output_label.emit(f"Loading PSD {label}/{self._selected_roi.getLabelCount()}")

            copy_roi: ors.ROI = ors.ROI()
            copy_roi.copyShapeFromStructuredGrid(self._selected_roi)
            self._selected_roi.addToVolumeROI(copy_roi, label)
            labels.append(label)
            names.append(self._selected_roi.getLabelName(label))

            self.update_output_label.emit(f"Processing PSD {label}/{self._selected_roi.getLabelCount()}")

            scale = scale_from_roi(copy_roi)

            cropped_roi_arr, original_translations = get_cropped_roi_arr(copy_roi, scale)

            output = processing.get_area(
                raw_data=cropped_roi_arr, scale=scale, visualize=self._visualize_steps,
                visualize_end=self._visualize_results, c_s=self._c_s, visualize_signal=self.show_visualization,
                dist_threshold=self._dist_threshold
            )

            if self._gen_dragonfly_mesh and output.psd_mesh is not None:
                ors_mesh = mesh_to_ors(output.psd_mesh, [original_translations, output.translations], scale)
                ors_mesh.setTitle(f"3D Pancake Output Mesh: {label}")
                ors_mesh.publish()

            outputs.append(output.area_microns())

            if self._compare_lindblad:
                self.update_output_label.emit(
                    f"Calculating Lindblad 2005 area for PSD {label}/{self._selected_roi.getLabelCount()}...")
                lindblad_2005.append(other_algorithms.surface_area_lindblad_2005(copy_roi))

            if self._compare_lewiner:
                self.update_output_label.emit(
                    f"Calculating Lewiner 2012 area for PSD {label}/{self._selected_roi.getLabelCount()}...")
                lewiner_2012.append(other_algorithms.surface_area_lewiner_2012(cropped_roi_arr, scale))

            copy_roi.deleteObject()

        self.update_output_label.emit(f"Completed {self._selected_roi.getLabelCount()} PSDs.")

        if self._output_filepath == "":
            return

        self._write_to_csv(names, outputs, labels, lindblad_2005, lewiner_2012)

    def run(self):
        try:
            if self._selected_roi is None:
                self.update_output_label.emit("No ROI selected")
                return

            self.update_output_label.emit("Processing...")

            if isinstance(self._selected_roi, ors.ROI):
                self.process_single_roi()
            else:
                self.process_multi_roi()

        except Exception as e:
            self.update_output_label.emit(f"Error: {e}")
            raise e
