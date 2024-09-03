import functools

from PyQt6.QtCore import QThread, pyqtSignal

from .processing import data
from typing import Union

from ORSModel import ors

import numpy as np
from .processing import processing

import multiprocessing as mp


# Since the visualization signal cannot be pickled, it cannot be passed to a multiprocessing process. This is a
#  workaround. It's not the most elegant solution, but it works.
global_vis_signal = None


def process_single_roi_worker(
        roi: ors.ROI, scale: data.Scale, visualize_steps: bool, visualize_results: bool, c_s: float
):
    min_indices = roi.getLocalBoundingBoxMin(0)
    min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()], dtype=int)[::-1]
    max_indices = roi.getLocalBoundingBoxMax(0)
    max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()], dtype=int)[::-1]

    roi_arr = roi.getAsNDArray()
    roi_arr = roi_arr[
              min_indices[0]:max_indices[0] + 1,
              min_indices[1]:max_indices[1] + 1,
              min_indices[2]:max_indices[2] + 1
              ]

    # Data processing
    output = processing.get_area(
        roi_arr,
        scale=scale,
        visualize=visualize_steps,
        visualize_end=visualize_results,
        c_s=c_s,
        visualize_signal=global_vis_signal
    )

    area_um = output.area_nm / 1e6

    return f"Area: {area_um:.6f} μm²"


class PancakeWorker(QThread):
    """
    The Pancake Worker class. Allows the surface area to be processed in the background.
    """

    update_output_label = pyqtSignal(str)
    show_visualization = pyqtSignal(functools.partial)

    def __init__(self, selected_roi: Union[None, ors.ROI, ors.MultiROI],
                 scale: data.Scale, visualize_steps: bool, visualize_results: bool, c_s: float):
        """
        Initializes the Pancake Worker.

        :param selected_roi: The ROI or MultiROI to process. If none, the worker will not run.
        :param scale: The scale of the data
        :param visualize: Whether to visualize each step
        :param c_s: The c_s value. How tight a fit the surface is to the data.
        """
        global global_vis_signal

        super().__init__()

        self._selected_roi = selected_roi
        self._scale = scale
        self._visualize_steps = visualize_steps
        self._visualize_results = visualize_results
        self._c_s = c_s

        global_vis_signal = self.show_visualization

    def process_single_roi(self):
        output = process_single_roi_worker(self._selected_roi, self._scale, self._visualize_steps,
                                           self._visualize_results, self._c_s)
        self.update_output_label.emit(output)

    def process_multi_roi(
            self, multi_roi: ors.MultiROI, scale: data.Scale, visualize_steps: bool, visualize_results: bool, c_s: float
    ):
        # TODO: figure out why all these parameters are passed. Do they need to be?

        single_rois: list[ors.ROI] = []

        for label_index in range(1, self._selected_roi.getLabelCount() + 1):
            copy_roi = ors.ROI()
            copy_roi.copyShapeFromStructuredGrid(multi_roi)
            multi_roi.addToVolumeROI(copy_roi, label_index)

            single_rois.append(copy_roi)

        partial_func = functools.partial(
            process_single_roi_worker,
            scale=scale,
            visualize_steps=visualize_steps,
            visualize_results=visualize_results,
            c_s=c_s
        )

        with mp.Pool() as pool:
            self.update_output_label.emit("Processing...")
            result = pool.map(partial_func, single_rois)

        self.update_output_label.emit("Done")

    def run(self):
        try:
            if self._selected_roi is None:
                self.update_output_label.emit("No ROI selected")
                return

            self.update_output_label.emit("Processing...")

            if isinstance(self._selected_roi, ors.ROI):
                self.process_single_roi()
            else:
                self.process_multi_roi(
                    self._selected_roi,
                    self._scale,
                    self._visualize_steps,
                    self._visualize_results,
                    self._c_s
                )

        except Exception as e:
            self.update_output_label.emit(f"Error: {e}")
            raise e
