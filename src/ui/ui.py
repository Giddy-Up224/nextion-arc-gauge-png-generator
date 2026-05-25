from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QIcon, QPixmap
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arc Generator")
        self.setWindowIcon(QIcon('img/R.png'))
        self.statusBar().showMessage('Have fun!')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vbox = QVBoxLayout()
        central_widget.setLayout(vbox)
        self.img_viewer = QGraphicsView()
        vbox.addWidget(self.img_viewer)
        self.display_image('test/test.png')


    def display_image(self, pil_image):
        from PIL.ImageQt import ImageQt
        qt_image = ImageQt(pil_image)
        pixmap = QPixmap.fromImage(qt_image)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.img_viewer.setScene(scene)