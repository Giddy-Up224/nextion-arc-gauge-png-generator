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
        self.setFixedSize(70, 25)
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

class ArcControls(QGroupBox):
    def __init__(self, title: str):
        super().__init__()
        self.setTitle(title)
        layout = QGridLayout(self)
        self.bg_color = QLabel('Arc Color:')
        layout.addWidget(self.bg_color, 0, 0)
        self.bg_color_btn = ColorButton(QColor('#555555'))
        layout.addWidget(self.bg_color_btn, 0, 1)
        self.endcap_color = QLabel('Endcap Color:')
        layout.addWidget(self.endcap_color, 1, 0)
        self.endcap_color_btn = ColorButton(QColor('#555555'))
        layout.addWidget(self.endcap_color_btn, 1, 1)