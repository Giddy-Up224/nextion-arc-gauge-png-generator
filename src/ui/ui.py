from PySide6.QtCore import Qt, Slot, QIODevice
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from PySide6.QtWidgets import QTabWidget, QTextEdit, QGridLayout, QButtonGroup, QLineEdit, QGroupBox, QColorDialog, QFileDialog
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QIcon
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arc Generator")
        self.setWindowIcon(QIcon('img/R.png'))
        self.statusBar().showMessage('Have fun!')
        # Create the main widget and set it as the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the main widget
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Create a tab widget and add it to the main layout
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_tab1()
        self.create_tab2()

    def create_tab1(self):
        tab1 = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("This is Tab 1")
        layout.addWidget(label)
        
        button = QPushButton("Click Me")
        layout.addWidget(button)
        
        tab1.setLayout(layout)
        self.tab_widget.addTab(tab1, "Tab 1")

    def create_tab2(self):
        tab2 = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("This is Tab 2")
        layout.addWidget(label)
        
        text_edit = QTextEdit()
        layout.addWidget(text_edit)
        
        tab2.setLayout(layout)
        self.tab_widget.addTab(tab2, "Tab 2")