from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtGui import QColor


class FolderPath(QGroupBox):
    def __init__(self, path='src/preview'):
        super().__init__()
        self.path = path
        self.setTitle('File')
        layout = QGridLayout(self)
        self.filepath_lbl = QLabel('File:')
        self.filepath_fld = QLineEdit()
        self.filepath_fld.setFixedWidth(200)
        self.file_browse_btn = QPushButton()
        self.file_browse_btn.setText('Browse...')
        self.file_browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.file_browse_btn, 0, 1)
        layout.addWidget(self.filepath_lbl,    1, 0)
        layout.addWidget(self.filepath_fld,    1, 1)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, 'Choose Destination Folder', self.path)
        return path



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

    def open_color_picker(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")
        if color.isValid():
            self.color = color
            self.update_color(self.color)

    def get_color(self):
        print(f"type: {type(QColor(self.color).getRgb())}")
        return QColor(self.color).getRgb()

class ArcControls(QGroupBox):
    def __init__(self, title: str):
        super().__init__()
        self.setTitle(title)
        layout = QGridLayout(self)
        # Background arc color selection
        self.color_btn_lbl    = QLabel('Arc Color:')
        self.btn_color        = ColorButton(QColor('#FFFFFF'))
        self.endcap_color_lbl = QLabel('Endcap Color:')
        self.endcap_btn_color = ColorButton(QColor('#FFFFFF'))
        layout.addWidget(self.color_btn_lbl,    0, 0)
        layout.addWidget(self.btn_color,        0, 1)
        layout.addWidget(self.endcap_color_lbl, 1, 0)
        layout.addWidget(self.endcap_btn_color, 1, 1)