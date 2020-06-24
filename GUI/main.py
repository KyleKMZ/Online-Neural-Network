import sys
sys.path.append('../Scripts/')
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from MainWindow import Ui_MainWindow
from parse_particles import parse_particles

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.importStarBtn.clicked.connect(self.import_star_file)
        self.importCsBtn.clicked.connect(self.import_cs_file)
 
    def import_star_file(self):
        fname, ok = QFileDialog.getOpenFileName(self, 'Select a Relion STAR file', '', 'Relion STAR file (*.star)') 
        if fname and ok:
            text, ok = QInputDialog.getText(self, "Entry Name", "Enter name of data entry", QLineEdit.Normal, QDir().home().dirName())
            if text and ok:
                entry_name = text
                parse_particles(fname, entry_name)

    def import_cs_file(self):
        fname, ok = QFileDialog.getOpenFileName(self, 'Select a Cryosparc particle file', '', 'Cryosparc CS file (*.cs)')
        if fname and ok: 
            text, ok = QInputDialog.getText(self, "Entry Name", "Enter name of data entry", QLineEdit.Normal, QDir().home().dirName())
            if text and ok:
                entry_name = text
                parse_particles(fname, entry_name)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
