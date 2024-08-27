from PyQt6.QtWidgets import QLineEdit, QApplication
from PyQt6.QtCore import Qt


class CopyableLabel(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("hi there hello initialized")
        self.setReadOnly(True)  # Make it read-only
        self.setFrame(False)  # Remove the border to make it look like a label
        self.setStyleSheet("background: transparent;")  # Transparent background to mimic QLabel
        self.setStyleSheet("border: none;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
