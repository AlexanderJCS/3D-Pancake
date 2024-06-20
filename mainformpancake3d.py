import ORSModel
from ORSModel import orsObj, ROI, MultiROI
from ORSServiceClass.ORSWidget.chooseObjectAndNewName.chooseObjectAndNewName import ChooseObjectAndNewName
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6 import QtGui

from OrsLibraries.workingcontext import WorkingContext
from ORSServiceClass.windowclasses.orsabstractwindow import OrsAbstractWindow
from PyQt6.QtWidgets import QDialog

from .ui_mainformpancake3d import Ui_MainFormPancake3D

from typing import Optional
from typing import Union

from processing import processing
from processing import data
import numpy as np


class MainFormPancake3D(OrsAbstractWindow):

    def __init__(self, implementation, parent=None):
        super().__init__(implementation, parent)
        self.ui = Ui_MainFormPancake3D()
        self.ui.setupUi(self)

        self.ui.line_edit_c_s.setValidator(QtGui.QDoubleValidator(0, 100, 6))
        self.ui.line_edit_xy_scale.setValidator(QtGui.QDoubleValidator(0, 10000, 6))
        self.ui.line_edit_z_scale.setValidator(QtGui.QDoubleValidator(0, 10000, 6))


        WorkingContext.registerOrsWidget(
            "Pancake3D_eae430b521c411efa291f83441a96bd5",
            implementation,
            "MainFormPancake3D",
            self
        )

        self.selected_roi: Union[ROI, MultiROI, None] = None

    @staticmethod
    def roi_dialog(managed_class: Union[type[ROI], type[MultiROI]] = ROI) -> Optional:
        chooser = ChooseObjectAndNewName(
            managedClass=[managed_class],
            parent=WorkingContext.getCurrentContextWindow()
        )

        chooser.setWindowTitle("Select an ROI")
        chooser.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
        )

        if chooser.exec() == QDialog.DialogCode.Rejected:
            return None

        guid = chooser.getObjectGUID()
        roi = orsObj(guid)

        return roi

    def select_roi(self, managed_class: Union[type[ROI], type[MultiROI]]):
        roi: Optional[managed_class] = self.roi_dialog(managed_class)

        if roi is None:
            return

        self.selected_roi = roi
        self.ui.label_selected.setText(f"Selected: {roi.getTitle()}")

    @pyqtSlot()
    def on_btn_select_roi_clicked(self):
        self.select_roi(ROI)

    @pyqtSlot()
    def on_btn_select_multiroi_clicked(self):
        self.select_roi(MultiROI)

    def process_single_roi(self, roi: ROI):
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
        processing.get_area(
            roi_arr,
            scale=data.Scale(float(self.ui.line_edit_xy_scale.text()), float(self.ui.line_edit_z_scale.text())),
            visualize=self.ui.chk_visualize.isChecked(),
            c_s=float(self.ui.line_edit_c_s.text())
        )

    def process_multi_roi(self, multi_roi: MultiROI, scale: data.Scale):
        roi_arr = multi_roi.getAsNDArray()

        for label in range(1, multi_roi.getLabelCount() + 1):
            label_bounding_box: ORSModel.Box = multi_roi.getBoundingBoxOfLabel(0, label)

            min_indices: ORSModel.ors.Vector3 = label_bounding_box.getSummitmmm()
            max_indices: ORSModel.ors.Vector3 = label_bounding_box.getSummitppp()

            min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()])[::-1]
            max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()])[::-1]

            min_indices *= 1e9  # meters to nm
            max_indices *= 1e9

            min_indices /= scale.zyx()
            max_indices /= scale.zyx()

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
            print(new_arr)

    @pyqtSlot()
    def on_btn_process_clicked(self):
        # TODO: Add error handling for invalid scale input

        if self.selected_roi is None:
            self.ui.label_output.setText("No ROI selected")
            return

        if isinstance(self.selected_roi, ROI):
            self.process_single_roi(self.selected_roi)
        else:
            self.process_multi_roi(
                self.selected_roi,
                data.Scale(float(self.ui.line_edit_xy_scale.text()), float(self.ui.line_edit_z_scale.text()))
            )
