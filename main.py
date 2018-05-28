from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QGroupBox, QLabel, QComboBox, QPushButton, QLineEdit, QHBoxLayout, \
    QVBoxLayout, QProgressBar

from PyQt5.Qt import pyqtSlot

from widgets.input_widget import InputWidget

import os
from threading import Thread
from datetime import datetime
from typing import Dict, List, Union, Tuple
from recipes import REGISTRY


class Main(QtWidgets.QMainWindow):

    TITLE = 'DasRezept'

    def __init__(self):
        super(Main, self).__init__()
        self.__init_gui()

    def __init_gui(self):
        self.setWindowTitle(self.TITLE)

        central_widget = QtWidgets.QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        recipe_selection = self._create_recipe_selection()
        central_layout.addWidget(recipe_selection)

        self._input_selectors = {}

        for key, cls in REGISTRY.items():
            widget = InputWidget(key, cls.inputs(), self)
            widget.hide()
            central_layout.addWidget(widget)
            self._input_selectors[key] = widget

        central_layout.addStretch(1)

        self._recipe_progress = QProgressBar(self)
        self._recipe_progress.setMaximum(100)
        self._recipe_progress.setMinimum(0)
        self._recipe_progress.setValue(0)

        central_layout.addWidget(self._recipe_progress)

        self.statusBar()
        self.statusBar().showMessage('ready')

        self.setCentralWidget(central_widget)
        self.setGeometry(500, 300, 500, 350)

    def _create_recipe_selection(self):
        group_box = QGroupBox('Recipe', self)
        layout = QHBoxLayout()
        group_box.setLayout(layout)

        self._recipe_combobox = QComboBox(group_box)
        self._recipe_combobox.addItem('...')
        self._recipe_combobox.currentTextChanged.connect(self._selection_changed)

        for key, cls in REGISTRY.items():
            self._recipe_combobox.addItem(key)

        self._recipe_run_button = QPushButton('run', group_box)
        self._recipe_stop_button = QPushButton('stop', group_box)

        self._recipe_run_button.setDisabled(True)
        self._recipe_stop_button.hide()

        layout.addWidget(self._recipe_combobox)
        layout.addStretch(1)
        layout.addWidget(self._recipe_run_button)
        layout.addWidget(self._recipe_stop_button)

        self._recipe_run_button.clicked.connect(self._on_run)
        self._recipe_stop_button.clicked.connect(self._on_stop)

        return group_box

    @pyqtSlot()
    def _on_stop(self):
        self._recipe_run_button.show()
        self._recipe_stop_button.hide()

    @pyqtSlot()
    def _on_run(self):
        self._recipe_run_button.hide()
        self._recipe_stop_button.show()

    @pyqtSlot()
    def _selection_changed(self):
        if self._recipe_combobox.itemText(0) == '...':
            self._recipe_combobox.removeItem(0)

        for key, widget in self._input_selectors.items():
            widget.hide()

        selected = self._recipe_combobox.currentText()

        self._input_selectors[selected].show()

        self._recipe_run_button.setEnabled(True)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    m = Main()
    m.show()
    sys.exit(app.exec_())
