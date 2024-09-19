# Form implementation generated from reading ui file '.\mainformpancake3d.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainFormPancake3D(object):
    def setupUi(self, MainFormPancake3D):
        MainFormPancake3D.setObjectName("MainFormPancake3D")
        MainFormPancake3D.resize(420, 440)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainFormPancake3D.sizePolicy().hasHeightForWidth())
        MainFormPancake3D.setSizePolicy(sizePolicy)
        MainFormPancake3D.setMinimumSize(QtCore.QSize(420, 440))
        self.verticalLayout = QtWidgets.QVBoxLayout(MainFormPancake3D)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(MainFormPancake3D)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_cs = QtWidgets.QLabel(MainFormPancake3D)
        self.label_cs.setObjectName("label_cs")
        self.horizontalLayout_2.addWidget(self.label_cs)
        self.line_edit_c_s = QtWidgets.QLineEdit(MainFormPancake3D)
        self.line_edit_c_s.setObjectName("line_edit_c_s")
        self.horizontalLayout_2.addWidget(self.line_edit_c_s)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_xy_scale = QtWidgets.QLabel(MainFormPancake3D)
        self.label_xy_scale.setObjectName("label_xy_scale")
        self.horizontalLayout.addWidget(self.label_xy_scale)
        self.line_edit_xy_scale = QtWidgets.QLineEdit(MainFormPancake3D)
        self.line_edit_xy_scale.setObjectName("line_edit_xy_scale")
        self.horizontalLayout.addWidget(self.line_edit_xy_scale)
        self.label_z_scale = QtWidgets.QLabel(MainFormPancake3D)
        self.label_z_scale.setObjectName("label_z_scale")
        self.horizontalLayout.addWidget(self.label_z_scale)
        self.line_edit_z_scale = QtWidgets.QLineEdit(MainFormPancake3D)
        self.line_edit_z_scale.setObjectName("line_edit_z_scale")
        self.horizontalLayout.addWidget(self.line_edit_z_scale)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(MainFormPancake3D)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.line_edit_file = QtWidgets.QLineEdit(MainFormPancake3D)
        self.line_edit_file.setObjectName("line_edit_file")
        self.horizontalLayout_4.addWidget(self.line_edit_file)
        self.btn_file_select = QtWidgets.QPushButton(MainFormPancake3D)
        self.btn_file_select.setObjectName("btn_file_select")
        self.horizontalLayout_4.addWidget(self.btn_file_select)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.line_edit_filepath = QtWidgets.QLineEdit(MainFormPancake3D)
        self.line_edit_filepath.setObjectName("line_edit_filepath")
        self.verticalLayout.addWidget(self.line_edit_filepath)
        self.label_3 = QtWidgets.QLabel(MainFormPancake3D)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_select_multiroi = QtWidgets.QPushButton(MainFormPancake3D)
        self.btn_select_multiroi.setObjectName("btn_select_multiroi")
        self.horizontalLayout_3.addWidget(self.btn_select_multiroi)
        self.btn_select_roi = QtWidgets.QPushButton(MainFormPancake3D)
        self.btn_select_roi.setObjectName("btn_select_roi")
        self.horizontalLayout_3.addWidget(self.btn_select_roi)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_selected = QtWidgets.QLabel(MainFormPancake3D)
        self.label_selected.setObjectName("label_selected")
        self.verticalLayout.addWidget(self.label_selected)
        self.label_4 = QtWidgets.QLabel(MainFormPancake3D)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.chk_visualize_steps = QtWidgets.QCheckBox(MainFormPancake3D)
        self.chk_visualize_steps.setObjectName("chk_visualize_steps")
        self.horizontalLayout_5.addWidget(self.chk_visualize_steps)
        self.chk_visualize_results = QtWidgets.QCheckBox(MainFormPancake3D)
        self.chk_visualize_results.setObjectName("chk_visualize_results")
        self.horizontalLayout_5.addWidget(self.chk_visualize_results)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.chk_compare_lewiner = QtWidgets.QCheckBox(MainFormPancake3D)
        self.chk_compare_lewiner.setWhatsThis("")
        self.chk_compare_lewiner.setObjectName("chk_compare_lewiner")
        self.horizontalLayout_6.addWidget(self.chk_compare_lewiner)
        self.chk_compare_lindblad = QtWidgets.QCheckBox(MainFormPancake3D)
        self.chk_compare_lindblad.setObjectName("chk_compare_lindblad")
        self.horizontalLayout_6.addWidget(self.chk_compare_lindblad)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.btn_process = QtWidgets.QPushButton(MainFormPancake3D)
        self.btn_process.setObjectName("btn_process")
        self.verticalLayout.addWidget(self.btn_process)
        self.label_output = CopyableLabel(MainFormPancake3D)
        self.label_output.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.IBeamCursor))
        self.label_output.setText("")
        self.label_output.setObjectName("label_output")
        self.verticalLayout.addWidget(self.label_output)

        self.retranslateUi(MainFormPancake3D)
        QtCore.QMetaObject.connectSlotsByName(MainFormPancake3D)

    def retranslateUi(self, MainFormPancake3D):
        _translate = QtCore.QCoreApplication.translate
        MainFormPancake3D.setWindowTitle(_translate("MainFormPancake3D", "3D Pancake"))
        self.label_2.setText(_translate("MainFormPancake3D", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Parameters</span></p></body></html>"))
        self.label_cs.setText(_translate("MainFormPancake3D", "<html><head/><body><p>cs (lower = tighter fit)</p></body></html>"))
        self.line_edit_c_s.setText(_translate("MainFormPancake3D", "0.67"))
        self.label_xy_scale.setText(_translate("MainFormPancake3D", "XY Scale (nm):"))
        self.line_edit_xy_scale.setText(_translate("MainFormPancake3D", "5.03"))
        self.label_z_scale.setText(_translate("MainFormPancake3D", "Z Scale (nm):"))
        self.line_edit_z_scale.setText(_translate("MainFormPancake3D", "42.017"))
        self.label.setText(_translate("MainFormPancake3D", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Output</span></p></body></html>"))
        self.line_edit_file.setPlaceholderText(_translate("MainFormPancake3D", "CSV File Name"))
        self.btn_file_select.setToolTip(_translate("MainFormPancake3D", "Select Folder"))
        self.btn_file_select.setText(_translate("MainFormPancake3D", "Select Output Folder"))
        self.line_edit_filepath.setPlaceholderText(_translate("MainFormPancake3D", "Output Filepath"))
        self.label_3.setText(_translate("MainFormPancake3D", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Input</span></p></body></html>"))
        self.btn_select_multiroi.setText(_translate("MainFormPancake3D", "Select Multiple PSDs (MultiROI)"))
        self.btn_select_roi.setText(_translate("MainFormPancake3D", "Select Single PSD (ROI)"))
        self.label_selected.setText(_translate("MainFormPancake3D", "Selected: None"))
        self.label_4.setText(_translate("MainFormPancake3D", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Debug</span></p></body></html>"))
        self.chk_visualize_steps.setToolTip(_translate("MainFormPancake3D", "Visualize each step of the algorithm in a new window. Not recommended for regular use or with processing MultiROIs."))
        self.chk_visualize_steps.setText(_translate("MainFormPancake3D", "Visualize Steps"))
        self.chk_visualize_results.setToolTip(_translate("MainFormPancake3D", "Visualize the final step of the algorithm in a new window. Not recommended for regular use or with processing MultiROIs."))
        self.chk_visualize_results.setText(_translate("MainFormPancake3D", "Visualize Final Step"))
        self.chk_compare_lewiner.setToolTip(_translate("MainFormPancake3D", "Add a column in the output CSV of the surface area as predicted by the Lewiner 2012 Marching Cubes algorithm"))
        self.chk_compare_lewiner.setText(_translate("MainFormPancake3D", "Compare area to Lewiner 2012"))
        self.chk_compare_lindblad.setToolTip(_translate("MainFormPancake3D", "Add a column in the output CSV of the surface area as predicted by the Lindblad 2005 algorithm"))
        self.chk_compare_lindblad.setText(_translate("MainFormPancake3D", "Compare area to Lindblad 2005"))
        self.btn_process.setText(_translate("MainFormPancake3D", "Process"))
from .copyable_label import CopyableLabel


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainFormPancake3D = QtWidgets.QWidget()
    ui = Ui_MainFormPancake3D()
    ui.setupUi(MainFormPancake3D)
    MainFormPancake3D.show()
    sys.exit(app.exec())
