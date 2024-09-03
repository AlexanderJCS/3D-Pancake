from ORSModel import orsObj, ROI, MultiROI
from ORSServiceClass.ORSWidget.chooseObjectAndNewName.chooseObjectAndNewName import ChooseObjectAndNewName
from PyQt6.QtCore import pyqtSlot, Qt, QRegularExpression
from PyQt6 import QtGui
from PyQt6.QtWidgets import QFileDialog

from OrsLibraries.workingcontext import WorkingContext
from ORSServiceClass.windowclasses.orsabstractwindow import OrsAbstractWindow
from PyQt6.QtWidgets import QDialog

from .ui_mainformpancake3d import Ui_MainFormPancake3D

from typing import Optional
from typing import Union
import threading
import os

from .processing import data
from . import pancake_worker


class MainFormPancake3D(OrsAbstractWindow):

    def __init__(self, implementation, parent=None):
        super().__init__(implementation, parent)

        self.ui = Ui_MainFormPancake3D()
        self.ui.setupUi(self)

        self.ui.line_edit_file.setValidator(QtGui.QRegularExpressionValidator(QRegularExpression(r"^[\w\-. ]+$")))
        self.ui.line_edit_file.textChanged.connect(self.on_line_edit_file_textChanged)

        self.ui.chk_visualize_steps.stateChanged.connect(self.on_chk_visualize_steps_stateChanged)

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

        self.worker_thread = None

        self.selected_filepath_dir: str = ""
        self.selected_filepath_name: str = ""

        self.visualization_lock = threading.Lock()

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

    @pyqtSlot(str)
    def update_output_label(self, text: str):
        self.ui.label_output.setText(text)

    @pyqtSlot()
    def on_btn_select_roi_clicked(self):
        self.select_roi(ROI)

    @pyqtSlot()
    def on_btn_select_multiroi_clicked(self):
        self.select_roi(MultiROI)

    def visualize_signal(self, function):
        function()

    @pyqtSlot()
    def on_btn_process_clicked(self):
        # TODO: Add error handling for invalid scale input (e.g., negative values)

        xy_scale = float(self.ui.line_edit_xy_scale.text())
        z_scale = float(self.ui.line_edit_z_scale.text())

        if xy_scale == 0 or z_scale == 0:
            self.ui.label_output.setText("Scale must be nonzero")
            return

        c_s = float(self.ui.line_edit_c_s.text())

        visualize_steps = self.ui.chk_visualize_steps.isChecked()
        visualize_results = self.ui.chk_visualize_results.isChecked()

        self.worker_thread = pancake_worker.PancakeWorker(self.selected_roi, data.Scale(xy_scale, z_scale), visualize_steps, visualize_results, c_s)
        self.worker_thread.update_output_label.connect(self.update_output_label)
        self.worker_thread.show_visualization.connect(self.visualize_signal)
        self.worker_thread.start()

    def refresh_file_path(self):
        self.ui.line_edit_filepath.setText(
            os.path.join(self.selected_filepath_dir, f"{self.selected_filepath_name}.csv").replace("\\", "/")
        )

    @pyqtSlot()
    def on_chk_visualize_steps_stateChanged(self):
        if self.ui.chk_visualize_steps.isChecked():
            self.ui.chk_visualize_results.setChecked(True)
            self.ui.chk_visualize_results.setEnabled(False)
        else:
            self.ui.chk_visualize_results.setEnabled(True)
            self.ui.chk_visualize_results.setChecked(False)

    @pyqtSlot()
    def on_btn_file_select_clicked(self):
        dialog = QFileDialog(self)
        # make dialog only accept folders
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_filepath_dir = dialog.selectedFiles()[0]
            self.refresh_file_path()

    @pyqtSlot()
    def on_line_edit_file_textChanged(self):
        self.selected_filepath_name = self.ui.line_edit_file.text()
        self.refresh_file_path()

    def update_label_output(self, text: str):
        self.ui.label_output.setText(text)
