from PyQt5.QtWidgets import QApplication, QGroupBox, QComboBox, QPushButton, QHBoxLayout, \
    QVBoxLayout, QProgressBar, QMessageBox, QMainWindow, QWidget, QStatusBar, QLabel
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from widgets.input_widget import InputWidget

from paho.mqtt.client import Client as MQTTClient

from threading import Thread
from recipes import REGISTRY
from recipes.recipe import SignalInterface

from datetime import datetime


class QtSignalInterface(SignalInterface, QObject):
    finished = pyqtSignal()
    started = pyqtSignal()
    stopped = pyqtSignal()
    status_message = pyqtSignal(str)
    update_process_value = pyqtSignal(int)

    def emit_finished(self) -> None:
        self.finished.emit()

    def emit_started(self) -> None:
        self.started.emit()

    def emit_stopped(self) -> None:
        self.stopped.emit()

    def emit_status_message(self, message: str) -> None:
        self.status_message.emit(message)

    def emit_update_process_value(self, value:int) -> None:
        self.update_process_value.emit(value)


class Main(QMainWindow):

    TITLE = 'DasRezept'

    def __init__(self):
        super(Main, self).__init__()

        self._running_recipe = None
        self._recipe_started_timestamp = None

        self.__init_gui()
        self.__init_mqtt_client()
        self.__init_signal_interface()

    def __init_gui(self):
        self.setWindowTitle(self.TITLE)

        central_widget = QWidget()
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

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        status_widget = QWidget(self._status_bar)
        self._status_bar.addWidget(status_widget, 1)

        status_horizontal_layout = QHBoxLayout()
        status_widget.setLayout(status_horizontal_layout)

        self._message_label = QLabel('', status_widget)
        self._etc_label = QLabel('', status_widget)

        status_horizontal_layout.addWidget(self._message_label)
        status_horizontal_layout.addStretch(1)
        status_horizontal_layout.addWidget(self._etc_label)

        self.setCentralWidget(central_widget)
        self.setGeometry(500, 300, 500, 350)

    def _create_recipe_selection(self):
        group_box = QGroupBox('Recipe', self)
        layout = QHBoxLayout()
        group_box.setLayout(layout)

        self._recipe_combobox = QComboBox(group_box)
        self._recipe_combobox.setDisabled(True)
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

    def __init_mqtt_client(self):
        self._mqtt_client = MQTTClient()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message

        self._mqtt_client.username_pw_set('ald', 'ald2017')
        try:
            self._mqtt_client.connect('ald', 1883, 60)
        except ConnectionRefusedError:
            QMessageBox.warning(self, 'Connection Failed','Connection to MQTT Server failed')
            exit(0)
        self._mqtt_client.loop_start()

    def __init_signal_interface(self):
        self._signal_interface = QtSignalInterface()
        self._signal_interface.finished.connect(self._on_recipe_finished)
        self._signal_interface.started.connect(self._on_recipe_started)
        self._signal_interface.stopped.connect(self._on_recipe_stopped)
        self._signal_interface.status_message.connect(self._on_status_message)
        self._signal_interface.update_process_value.connect(self._on_update_process_value)

    def _on_connect(self, client, userdata, flags, rc):
        self._recipe_combobox.setEnabled(True)

    def _on_message(self, client, userdata, msg):
        print('DEBUG(MQTT)', msg.payload)

    @pyqtSlot()
    def _on_stop(self):
        self._recipe_stop_button.hide()
        self._running_recipe.stop()
        self._recipe_run_button.show()
        self._recipe_run_button.setDisabled(True)

    @pyqtSlot()
    def _on_run(self):
        self._recipe_run_button.hide()
        self._recipe_stop_button.show()

        recipe_text = self._recipe_combobox.currentText()
        inputs = self._input_selectors[recipe_text].user_inputs
        cls = REGISTRY[recipe_text]

        self._running_recipe = cls(self._mqtt_client, self._signal_interface, **inputs)

        thread = Thread(target=self._running_recipe)
        thread.start()

    @pyqtSlot()
    def _selection_changed(self):
        if self._recipe_combobox.itemText(0) == '...':
            self._recipe_combobox.removeItem(0)

        self._hide_all_user_inputs()

        selected = self._recipe_combobox.currentText()

        self._input_selectors[selected].show()

        self._recipe_run_button.setEnabled(True)

    def _hide_all_user_inputs(self):
        for key, widget in self._input_selectors.items():
            widget.hide()

    @pyqtSlot()
    def _on_recipe_finished(self):
        self._show_status_bar_message('recipe finished')
        self._recipe_stop_button.hide()
        self._recipe_run_button.show()
        self._recipe_run_button.setEnabled(True)
        self._running_recipe = None

    @pyqtSlot()
    def _on_recipe_started(self):
        self._recipe_started_timestamp = datetime.now()
        self._show_status_bar_message('recipe started')

    @pyqtSlot()
    def _on_recipe_stopped(self):
        self._show_status_bar_message('recipe stopped')

    @pyqtSlot(str)
    def _on_status_message(self, message):
        self._show_status_bar_message(message)

    @pyqtSlot(int)
    def _on_update_process_value(self, value):
        max_value = self._running_recipe.max_process_value()
        self._recipe_progress.setMinimum(0)
        self._recipe_progress.setMaximum(max_value)
        self._recipe_progress.setValue(value)

        diff = datetime.now() - self._recipe_started_timestamp

        if value == 0:
            self._estimated_end = None
        else:
            self._estimated_end = datetime.now() + diff / value * max_value

        estimated_text = ''
        if self._estimated_end is not None:
            estimated_text = 'ETC: {:%H:%M}'.format(self._estimated_end)

        self._etc_label.setText(estimated_text)

    def _show_status_bar_message(self, message):
        text = '{:%H:%M:%S} - {}'.format(datetime.now(), message)
        self._message_label.setText(text)

    def closeEvent(self, *args, **kwargs):
        if self._running_recipe is not None:
            self._running_recipe.stop()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    m = Main()
    m.show()
    sys.exit(app.exec_())
