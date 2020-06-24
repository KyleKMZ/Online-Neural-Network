from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from MainWindow import Ui_MainWindow
import sys

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.importStarBtn.clicked.connect(self.import_star_file)
        self.importCsBtn.clicked.connect(self.import_cs_file)
 
    def import_star_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a Relion STAR file', '', 'Relion STAR file (*.star)') 

    def import_cs_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a Cryosparc particle file', '', 'Cryosparc CS file (*.cs)') 
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
