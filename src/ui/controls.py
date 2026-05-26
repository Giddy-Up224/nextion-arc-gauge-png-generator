from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtGui import QColor


class ColorButton(QPushButton):
    def __init__(self, color=QColor('#FFFFFF')):
        super().__init__()
        self.color = color
        btn_layout = QHBoxLayout(self)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignCenter) # type: ignore[attr-defined]
        self.color_btn_swatch = QLabel()
        self.color_btn_swatch.setFixedSize(48, 12)
        btn_layout.addWidget(self.color_btn_swatch)
        self.update_color(self.color)
        self.clicked.connect(self.open_color_picker)

    def update_color(self, color):
        # Set button background to current color
        self.color = color 
        color_name = QColor(self.color).name()
        self.color_btn_swatch.setStyleSheet(f"background-color: {color_name};")
        print(f"Color: {QColor(self.color).getRgb()}")

    def open_color_picker(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")
        if color.isValid():
            self.color = color
            self.update_color(self.color)


class Controls(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Arc Generator')
        layout = QGridLayout(self)
        # Color button
        self.color_btn = ColorButton(QColor(Qt.red)) # type: ignore[attr-defined]
        layout.addWidget(self.color_btn, 0, 0)