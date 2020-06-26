#/!/usr/bin/env python

import sys
sys.path.append('../Scripts/')
import os
import shutil
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from MainWindow import Ui_MainWindow
from parse_particles import parse_particles

class EntryDataModel(QAbstractListModel):
    def __init__(self, *args, entries=None, **kwargs):
        super(EntryDataModel, self).__init__(*args, **kwargs)
        self.entries = entries or []
        # Entries are stored as a list of dictionaries with each dict
        # having keys for 'entry_name', 'voltage', 'cs', 'amp_cont', 'psize', 'num_particles',
        # 'num_mics', 'entry_size' & 'date'

    def data(self, index, role):
        if role == Qt.DisplayRole:
            entry_name = self.entries[index.row()]['entry_name']
            entry_size = self.entries[index.row()]['entry_size']
            text = entry_name + ' (' + entry_size + ')'
            return text

    def rowCount(self, index):
        return len(self.entries)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.importStarBtn.clicked.connect(self.import_star_file)
        self.importCsBtn.clicked.connect(self.import_cs_file)
        self.deleteBtn.clicked.connect(self.delete_entry)
        self.entryModel = EntryDataModel()
        self.update_entry_model()
        self.entryListView.setModel(self.entryModel)
        self.entryListView.clicked.connect(self.update_metadata_info)
        self.setStyleSheet(open('stylesheet.css').read())
                
                        
 
    def import_star_file(self):
        fname, ok = QFileDialog.getOpenFileName(self, 'Select a Relion STAR file', '', 'Relion STAR file (*.star)') 
        if fname and ok:
            text, ok = QInputDialog.getText(self, "Entry Name", "Enter name of data entry", QLineEdit.Normal, QDir().home().dirName())
            if text and ok:
                entry_name = text
                parse_particles(fname, entry_name)
                # to refresh because a new entry has been added
                self.update_entry_model()
                self.entryModel.layoutChanged.emit()

    def import_cs_file(self):
        fname, ok = QFileDialog.getOpenFileName(self, 'Select a Cryosparc particle file', '', 'Cryosparc CS file (*.cs)')
        if fname and ok: 
            text, ok = QInputDialog.getText(self, "Entry Name", "Enter name of data entry", QLineEdit.Normal, QDir().home().dirName())
            if text and ok:
                entry_name = text
                parse_particles(fname, entry_name)
                # to refresh because a new entry has been added
                self.update_entry_model()

    def update_entry_model(self):
        self.entryModel.entries = []
        entries = [f.path for f in os.scandir('../Database/') if f.is_dir()]
        if entries:
            for entry in entries:
                with open(os.path.join(entry, 'info.txt'), 'r') as info_f:
                    num_particles = info_f.readline().split()[-1]
                    num_mics = info_f.readline().split()[-1]
                    voltage = info_f.readline().split()[-1]
                    cs = info_f.readline().split()[-1]
                    amp_cont = info_f.readline().split()[-1]
                    psize = info_f.readline().split()[-1]
                    
                    db_entry = {}
                    db_entry['entry_name'] = os.path.split(entry)[-1]
                    db_entry['num_particles'] = num_particles
                    db_entry['num_mics'] = num_mics
                    db_entry['voltage'] = voltage
                    db_entry['cs'] = cs
                    db_entry['amp_cont'] = amp_cont
                    db_entry['psize'] = psize
                    db_entry['entry_size'] = self.get_size_format(self.get_directory_size(entry))
                    self.entryModel.entries.append(db_entry)

        self.entryModel.layoutChanged.emit()

    def update_metadata_info(self):
        indexes = self.entryListView.selectedIndexes()
        if indexes:
            selected_entry = self.entryModel.entries[indexes[0].row()]
            self.voltageValue.setText(selected_entry['voltage'])
            self.csValue.setText(selected_entry['cs'])
            self.psizeValue.setText(selected_entry['psize'])
            self.doseValue.setText(selected_entry['amp_cont'])
            self.numParticlesLabel.setText(selected_entry['num_particles'])
            self.numMicsLabel.setText(selected_entry['num_mics'])

    def delete_entry(self):
        indexes = self.entryListView.selectedIndexes()
        if indexes:
            entry_name = self.entryModel.entries[indexes[0].row()]['entry_name']
            reply = QMessageBox.question(self, 'Delete Entry Confirmation', 
                    'Are you sure you want to the delete the entry: %s?' % entry_name)
            if (reply == QMessageBox.Yes):
                # Delete the entry directory in the database
                dir_path = os.path.join('../Database/', entry_name)
                shutil.rmtree(dir_path)
                self.update_entry_model()

    def get_directory_size(self, dir_path):
        total = 0
        try:
            for entry in os.scandir(dir_path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_directory_size(entry.path)
        
        except NotADirectoryError:
            return os.path.getsize(directory)

        except PermissionError:
            return 0

        return total

    def get_size_format(self, num_bytes, factor=1024, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if num_bytes < factor:
                return f"{num_bytes:.2f}{unit}{suffix}"
            num_bytes /= factor
        return f"{num_bytes:.2f}Y{suffix}"
 
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
