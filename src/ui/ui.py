from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QIcon, QPixmap, QColor
from .controls import ArcControls
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arc Generator")
        self.setWindowIcon(QIcon('img/R.png'))
        self.statusBar().showMessage('Have fun!')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        hbox = QHBoxLayout()
        central_widget.setLayout(hbox)
        self.img_viewer = QGraphicsView()
        hbox.addWidget(self.img_viewer)
        self.display_image('test/test.png')
        vbox = QVBoxLayout()
        hbox.addLayout(vbox)
        # Background arc
        self.bg_ctls = ArcControls('Background Arc')
        self.bg_ctls.btn_color.update_color('#75787B')
        self.bg_ctls.endcap_btn_color.update_color('#75787B')
        vbox.addWidget(self.bg_ctls)
        # Foreground arc
        self.fg_ctls = ArcControls('Foreground Arc')
        self.fg_ctls.btn_color.update_color('#FFC94D')
        self.fg_ctls.endcap_btn_color.update_color('#FFC94D')
        vbox.addWidget(self.fg_ctls)



    def display_image(self, pil_image):
        from PIL.ImageQt import ImageQt
        qt_image = ImageQt(pil_image)
        pixmap = QPixmap.fromImage(qt_image)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.img_viewer.setScene(scene)

    