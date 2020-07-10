#/!/usr/bin/env python

import sys
sys.path.append('../Scripts/')
import os
import shutil
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow
from file_crawler import parse_relion_project, parse_csparc_project
from file_crawler import parse_particles_cryoem_projects

class entryItem(QStandardItem):
        def __init(self, txt='', font_size=16, set_bold=True, color=QColor(255, 255, 255)):
                super().__init__()

                fnt = QFont('Open Sans', font_size)
                fnt.setBold(set_bold)

                self.setEditable(False)
                self.setForeground(color)
                self.setFont(fnt)
                self.setText(txt)

class subEntryItem(QStandardItem):
        def __init__(self, txt='', font_size=14, set_bold=False, color=QColor(255, 255, 255)):
                super().__init__()

                fnt = QFont('Open Sans', font_size)
                fnt.setBold(set_bold)

                self.setEditable(False)
                self.setForeground(color)
                self.setFont(fnt)
                self.setText(txt)

class dbModel(QStandardItemModel):
        def __init__(self, *args, entries=None, **kwargs):
                super(dbModel, self).__init__(*args, **kwargs)
                if entries:
                        self.entries = entries
                else:
                        self.entries = []

                
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.relionButton.clicked.connect(self.import_relion_project)
        self.csparcButton.clicked.connect(self.import_csparc_project)
        self.parserButton.clicked.connect(self.auto_parser)
        self.nnButton.clicked.connect(self.train_nn)
        self.pickButton.clicked.connect(self.pick_particles)

        self.dbModel = dbModel()
        self.update_dbModel()
        self.treeView.setModel(self.dbModel)
        self.treeView.clicked.connect(self.update_metadata_info)

    def import_relion_project(self):
            fname = QFileDialog.getExistingDirectory(self, 
                'Select a Relion project folder')
            if fname:
                text, ok = QInputDialog.getText(self, 'Entry Name',
                        'Enter name of entry')
                if text and ok:
                        entry_name = text
                        parse_relion_project(fname, entry_name)
                        self.update_dbModel()

    def import_csparc_project(self):
        fname = QFileDialog.getExistingDirectory(self,
                'Select a CSparc project folder')
        if fname:
                text, ok = QInputDialog.getText(self, 'Entry Name',
                        'Enter name of entry')
                if text and ok:
                        entry_name = text
                        parse_csparc_project(fname, entry_name)
                        self.update_dbModel()

    def auto_parser(self):
        dir_name = QFileDialog.getExistingDirectory(self,
                'Select the root folder')
        if dir_name:
                parse_particles_cryoem_projects(dir_name)

    def train_nn(self):
        pass

    def pick_particles(self):
        pass

    def update_dbModel(self):
        self.dbModel.entries = []
        entries = [os.path.join('../Database', f) for f in os.listdir('../Database') if
                os.path.isdir(os.path.join('../Database/', f))]

        for entry in entries:
                entryList = []
                entryName = os.path.basename(os.path.normpath(entry))
                entryList.append('%s %s' % (entryName, self.get_size_format(self.get_directory_size(entry))))
                
                particles_path = os.path.join(entry, 'Particles')
                subEntries = [os.path.join(particles_path, f) for f in os.listdir(particles_path) if os.path.isdir(os.path.join(particles_path, f))]
                for i in range(0, len(subEntries)):
                        entryList.append({})
                        with open(os.path.join(subEntries[i], 'info.txt'), 'r') as info_f:
                                num_particles = info_f.readline().split()[-1]
                                num_mics = info_f.readline().split()[-1]
                                voltage = info_f.readline().split()[-1]
                                cs = info_f.readline().split()[-1]
                                amp_cont = info_f.readline().split()[-1]
                                psize = info_f.readline().split()[-1]

                                entryList[i+1]['job_type'] = os.path.split(subEntries[i])[-1]
                                entryList[i+1]['num_particles'] = num_particles
                                entryList[i+1]['num_mics'] = num_mics
                                entryList[i+1]['voltage'] = voltage
                                entryList[i+1]['cs'] = cs
                                entryList[i+1]['amp_cont'] = amp_cont
                                entryList[i+1]['psize'] = psize
                                entryList[i+1]['job_size'] = self.get_size_format(self.get_directory_size(subEntries[i]))
                self.dbModel.entries.append(entryList)

        rootItem = self.dbModel.invisibleRootItem()
        # Entries are stored as a list of lists, where each sublist
        # has its first element as the entry name and the following
        # elements as dictionaries containing keys for 'job_type', voltage', 'cs'
        # 'amp_cont', 'psize', 'num_mics', 'num_particles' and 'location'
        entries = self.dbModel.entries
        if entries:
                for entry in entries:
                        main_entry = entry[0]
                        sub_entries = entry[1:]

                        entry_node = entryItem(main_entry)
                        for sub_entry in sub_entries:
                                sub_entry_node = subEntryItem('%s %s' % (sub_entry['job_type'], sub_entry['job_size']))
                                print('%s %s' % (sub_entry['job_type'], sub_entry['job_size']))
                                entry_node.appendRow(sub_entry_node)

                        rootItem.appendRow(entry_node)


        self.dbModel.layoutChanged.emit()

    def update_metadata_info(self):
        index = self.treeView.currentIndex()
        print(index)

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
        sys.exit(app.exec_())

if __name__ == '__main__':
        main()
