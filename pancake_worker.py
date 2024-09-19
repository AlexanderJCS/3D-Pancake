import functools

from PyQt6.QtCore import QThread, pyqtSignal

from . import csv_output
from .processing import data
from typing import Union

from ORSModel import ors

import numpy as np
from .processing import processing
from . import other_algorithms


# Since the visualization signal cannot be pickled, it cannot be passed to a multiprocessing process. This is a
#  workaround. It's not the most elegant solution, but it works.
global_vis_signal = None


def get_cropped_roi_arr(roi: ors.ROI) -> np.ndarray:
    """
    Gets the cropped ROI array. The ROI is cropped to the bounding box of the ROI.

    :param roi: The ROI to crop
    :return: The cropped ROI array
    """

    roi_arr = roi.getAsNDArray()

    if roi_arr.shape == (0,):
        return roi_arr

    min_indices = roi.getLocalBoundingBoxMin(0)
    min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()], dtype=int)[::-1]
    max_indices = roi.getLocalBoundingBoxMax(0)
    max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()], dtype=int)[::-1]

    return roi_arr[
        min_indices[0]:max_indices[0] + 1,
        min_indices[1]:max_indices[1] + 1,
        min_indices[2]:max_indices[2] + 1
    ]


def process_single_roi(
        roi_arr_cropped: np.ndarray, scale: data.Scale, visualize_steps: bool,visualize_results: bool, c_s: float):
    """
    :param roi_arr_cropped: The cropped ROI array
    :param scale: The scale of the data.
    :param visualize_steps: Whether to visualize each step.
    :param visualize_results: Whether to visualize the final result.
    :param c_s: The c_s value. How tight a fit the surface is to the data.
    :return: The area of the ROI in um^2. If the ROI is empty, -1 is returned.
    """

    # Data processing
    output = processing.get_area(
        roi_arr_cropped,
        scale=scale,
        visualize=visualize_steps,
        visualize_end=visualize_results,
        c_s=c_s,
        visualize_signal=global_vis_signal
    )

    return output.area_nm / 1e6  # area in um^2


class PancakeWorker(QThread):
    """
    The Pancake Worker class. Allows the surface area to be processed in the background.
    """

    update_output_label = pyqtSignal(str)
    show_visualization = pyqtSignal(functools.partial)

    def __init__(self, selected_roi: Union[None, ors.ROI, ors.MultiROI],
                 scale: data.Scale, visualize_steps: bool, visualize_results: bool, c_s: float,
                 output_filepath: str):
        """
        Initializes the Pancake Worker.

        :param selected_roi: The ROI or MultiROI to process. If none, the worker will not run.
        :param scale: The scale of the data
        :param visualize_steps: Whether to visualize each step
        :param visualize_results: Whether to visualize the final result
        :param c_s: The c_s value. How tight a fit the surface is to the data.
        """
        global global_vis_signal

        super().__init__()

        self._selected_roi = selected_roi
        self._scale = scale
        self._visualize_steps = visualize_steps
        self._visualize_results = visualize_results
        self._c_s = c_s
        self._output_filepath = output_filepath

        global_vis_signal = self.show_visualization

    def _write_to_csv(self, labels: list[str], outputs: list[float]):
        try:
            csv_output.write_csv(self._output_filepath, labels, outputs)
        except (FileNotFoundError, IsADirectoryError, NotADirectoryError):
            self.update_output_label.emit("Error writing to file. Check the filepath.")
        except PermissionError:
            self.update_output_label.emit("Permission error writing to CSV. Is it open by another program?")

    def process_single_roi(self):
        cropped_roi_arr = get_cropped_roi_arr(self._selected_roi)

        output = process_single_roi(cropped_roi_arr, self._scale, self._visualize_steps,
                                    self._visualize_results, self._c_s)
        self.update_output_label.emit(f"Done. Area: {output:.6f} μm²")

        if self._output_filepath == "":
            return

        self._write_to_csv(labels=[self._selected_roi.getTitle()], outputs=[output])

    def process_multi_roi(self):
        labels = []
        outputs = []

        for label in range(1, self._selected_roi.getLabelCount() + 1):
            self.update_output_label.emit(f"Loading PSD {label}/{self._selected_roi.getLabelCount()}")

            copy_roi = ors.ROI()
            copy_roi.copyShapeFromStructuredGrid(self._selected_roi)
            self._selected_roi.addToVolumeROI(copy_roi, label)

            self.update_output_label.emit(f"Processing PSD {label}/{self._selected_roi.getLabelCount()}")

            labels.append(label)

            cropped_roi_arr = get_cropped_roi_arr(copy_roi)

            outputs.append(process_single_roi(cropped_roi_arr, self._scale, self._visualize_steps,
                                              self._visualize_results, self._c_s))

            copy_roi.deleteObject()

        self.update_output_label.emit(f"Completed {self._selected_roi.getLabelCount()} PSDs.")

        if self._output_filepath == "":
            return

        self._write_to_csv(labels, outputs)

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
