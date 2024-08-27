from PyQt6.QtCore import QThread, pyqtSlot, pyqtSignal

from .processing import data
from typing import Union

from ORSModel import ors

import numpy as np
from .processing import processing


class PancakeWorker(QThread):
    """
    The Pancake Worker class. Allows the surface area to be processed in the background.
    """

    update_output_label = pyqtSignal(str)

    def __init__(self, selected_roi: Union[None, ors.ROI, ors.MultiROI],
                 scale: data.Scale, visualize: bool, c_s: float):
        """
        Initializes the Pancake Worker.

        :param selected_roi: The ROI or MultiROI to process. If none, the worker will not run.
        :param scale: The scale of the data
        :param visualize: Whether to visualize each step
        :param c_s: The c_s value. How tight a fit the surface is to the data.
        """

        super().__init__()

        self._selected_roi = selected_roi
        self._scale = scale
        self._visualize = visualize
        self._c_s = c_s

    def process_single_roi(self):
        self._selected_roi: ors.ROI  # we can assume it's an ROI if this code is being run

        min_indices = self._selected_roi.getLocalBoundingBoxMin(0)
        min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()], dtype=int)[::-1]
        max_indices = self._selected_roi.getLocalBoundingBoxMax(0)
        max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()], dtype=int)[::-1]

        roi_arr = self._selected_roi.getAsNDArray()
        roi_arr = roi_arr[
                  min_indices[0]:max_indices[0] + 1,
                  min_indices[1]:max_indices[1] + 1,
                  min_indices[2]:max_indices[2] + 1
                  ]

        # Data processing
        output = processing.get_area(
            roi_arr,
            scale=self._scale,
            visualize=self._visualize,
            c_s=self._c_s
        )

        area_um = output.area_nm / 1e6
        self.update_output_label.emit(f"Area: {area_um:.6f} μm²")

    def process_multi_roi(self):
        self._selected_roi: ors.MultiROI  # we can assume it's a MultiROI if this code is being run

        roi_arr = self._selected_roi.getAsNDArray()

        for label in range(1, self._selected_roi.getLabelCount() + 1):
            label_bounding_box: ors.Box = self._selected_roi.getBoundingBoxOfLabel(0, label)

            min_indices: ors.Vector3 = label_bounding_box.getSummitmmm()
            max_indices: ors.Vector3 = label_bounding_box.getSummitppp()

            min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()])[::-1]
            max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()])[::-1]

            min_indices *= 1e9  # meters to nm
            max_indices *= 1e9

            min_indices /= self._scale.zyx()
            max_indices /= self._scale.zyx()

            min_indices = min_indices.astype(int)
            max_indices = max_indices.astype(int)

            new_arr = roi_arr[
                      min_indices[0]:max_indices[0] + 1,
                      min_indices[1]:max_indices[1] + 1,
                      min_indices[2]:max_indices[2] + 1
                      ]

            # Skip if the ROI is empty
            if new_arr.size == 0:
                continue

            print(new_arr.shape)
            print(np.max(new_arr))

        self.update_output_label.emit("Done")

    @pyqtSlot()
    def start(self):
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
