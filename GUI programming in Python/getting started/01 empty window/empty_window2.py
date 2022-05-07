import sys

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):


    def __init__(self):
        
        super().__init__()

        self.setWindowTitle("My App")
        self.setFixedSize(QSize(400,300))


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()