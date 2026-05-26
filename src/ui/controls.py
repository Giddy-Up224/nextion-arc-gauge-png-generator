from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtGui import QColor


class ColorButton(QPushButton):
    def __init__(self, color=Qt.white): # type: ignore[attr-defined]
        super().__init__()
        self.current_color = color
        btn_layout = QHBoxLayout(self)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignCenter) # type: ignore[attr-defined]
        self.color_btn_swatch = QLabel()
        self.color_btn_swatch.setFixedSize(48, 12)
        btn_layout.addWidget(self.color_btn_swatch)
        self.update_color(self.current_color)
        self.clicked.connect(self.open_color_picker)

    def update_color(self, color):
        # Set button background to current color
        self.current_color = color 
        color_name = QColor(self.current_color).name()
        self.color_btn_swatch.setStyleSheet(f"background-color: {color_name};")

    def open_color_picker(self):
        color = QColorDialog.getColor(self.current_color, self, "Select Color")
        if color.isValid():
            self.current_color = color
            self.update_color(self.current_color)


class Controls(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Arc Generator')
        layout = QGridLayout(self)
        # Color button
        self.color_btn = ColorButton(Qt.red) # type: ignore[attr-defined]
        layout.addWidget(self.color_btn, 0, 0)