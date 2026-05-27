from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QSpinBox
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtGui import QColor
import os
from pathlib import Path

        

class FolderPath(QGroupBox):
    def __init__(self, path=Path.joinpath(Path(__file__).parents[2], 'output')):
        super().__init__()
        self.output_path = path
        self.setTitle('File')
        layout = QGridLayout(self)
        self.filepath_lbl = QLabel('Output Folder:')
        self.filepath_fld = QLineEdit(text=str(path))
        self.filepath_fld.setFixedWidth(500)
        self.file_browse_btn = QPushButton()
        self.file_browse_btn.setText('Browse...')
        self.file_browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.filepath_lbl,    0, 0)
        layout.addWidget(self.filepath_fld,    0, 1)
        layout.addWidget(self.file_browse_btn, 0, 2)

    def browse_folder(self):
        if self.ensure_output_folder_exists():
            self.output_path = QFileDialog.getExistingDirectory(self, 'Choose Destination Folder', str(self.output_path))
    
    def ensure_output_folder_exists(self):
        if not Path(self.output_path).exists:
            try:
                Path(self.output_path).mkdir(exist_ok=True)
                return True
            except Exception as e:
                print(f"Exception creating folder! Exception: {e}")
                return False
        else:
            return True



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

class ArcDesignControls(QGroupBox):
    def __init__(self, title: str):
        super().__init__()
        self.setTitle(title)
        layout = QGridLayout(self)
        # Background arc color selection
        self.color_btn_lbl    = QLabel('Arc Color:')
        self.btn_color        = ColorButton(QColor('#FFFFFF'))
        self.endcap_color_lbl = QLabel('Endcap Color:')
        self.endcap_btn_color = ColorButton(QColor('#FFFFFF'))
        self.encaps_ckbx      = QCheckBox('Endcaps')
        self.encaps_ckbx.setChecked(True)
        self.start_angle_lbl  = QLabel('Start Angle:')
        self.start_angle_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.end_angle_lbl    = QLabel('End Angle:')
        self.end_angle_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.start_angle_fld  = QLineEdit()
        self.end_angle_fld    = QLineEdit()
        layout.addWidget(self.color_btn_lbl,    0, 0)
        layout.addWidget(self.btn_color,        0, 1)
        layout.addWidget(self.start_angle_lbl,  0, 2)
        layout.addWidget(self.start_angle_fld,  0, 3)
        layout.addWidget(self.encaps_ckbx,      0, 4)
        layout.addWidget(self.endcap_color_lbl, 1, 0)
        layout.addWidget(self.endcap_btn_color, 1, 1)
        layout.addWidget(self.end_angle_lbl,    1, 2)
        layout.addWidget(self.end_angle_fld,    1, 3)

class ArcCountControls(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        self.number_of_images_lbl = QLabel('No. of Images')
        self.number_of_images_fld = QSpinBox()
        self.number_of_images_fld.setValue(1)
        self.number_of_images_fld.setMaximum(500)
        layout.addWidget(self.number_of_images_lbl, 0, 0)
        layout.addWidget(self.number_of_images_fld, 0, 1)