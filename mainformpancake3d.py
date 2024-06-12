from ORSModel import orsObj, ROI
from ORSServiceClass.ORSWidget.chooseObjectAndNewName.chooseObjectAndNewName import ChooseObjectAndNewName
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6 import QtGui

from OrsLibraries.workingcontext import WorkingContext
from ORSServiceClass.windowclasses.orsabstractwindow import OrsAbstractWindow
from PyQt6.QtWidgets import QDialog

from .ui_mainformpancake3d import Ui_MainFormPancake3D

from typing import Optional

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

    @staticmethod
    def roi_dialog() -> Optional[ROI]:
        def acceptable_roi(roi_to_test: ROI):
            # The ROI should not be empty
            if roi_to_test.getVoxelCount(0) == 0:
                return False

            return True

        chooser = ChooseObjectAndNewName(
            managedClass=[ROI],
            parent=WorkingContext.getCurrentContextWindow(),
            filterFunction=acceptable_roi
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

    @pyqtSlot()
    def on_btn_process_clicked(self):
        roi: ROI = self.roi_dialog()

        if roi is None:
            return

        min_indices = roi.getLocalBoundingBoxMin(0)
        min_indices = np.array([min_indices.getX(), min_indices.getY(), min_indices.getZ()], dtype=int)[::-1]
        max_indices = roi.getLocalBoundingBoxMax(0)
        max_indices = np.array([max_indices.getX(), max_indices.getY(), max_indices.getZ()], dtype=int)[::-1]

        roi_arr = roi.getNDArray()
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
