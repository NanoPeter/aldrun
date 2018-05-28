from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, QScrollArea
from PyQt5.Qt import QFrame
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from recipes.recipe import FloatValue, IntegerValue


class InputWidget(QScrollArea):
    def __init__(self, name, inputs, parent='None'):
        super().__init__(parent)
        self._input_widgets = {}
        self._inputs = inputs
        self._init_group_box(name)

    def _init_group_box(self, name):

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        group_box = QGroupBox(name, self)
        self.setWidget(group_box)

        vertical_layout = QVBoxLayout()
        group_box.setLayout(vertical_layout)

        for key, value in self._inputs.items():
            widget = self._create_input(key, value, parent=group_box)
            vertical_layout.addWidget(widget)

        if len(self._inputs.keys()) == 0:
            label = QLabel('Recipe does not require any inputs.', self)
            vertical_layout.addWidget(label)

    def _create_input(self, short_name: str, value, parent=None):
        if not parent:
            parent = self

        widget = QWidget(parent)
        horizontal_layout = QHBoxLayout()

        label = QLabel('{}:'.format(value.fullname), widget)
        horizontal_layout.addWidget(label)
        horizontal_layout.addStretch(1)

        input_widget = QLineEdit(widget)
        if isinstance(value, FloatValue):
            input_widget.setValidator(QDoubleValidator())
        elif isinstance(value, IntegerValue):
            input_widget.setValidator(QIntValidator())


        horizontal_layout.addWidget(input_widget)

        self._input_widgets[short_name] = input_widget

        input_widget.setText(str(value.default))

        widget.setLayout(horizontal_layout)
        return widget

    @property
    def user_inputs(self):
        result = {}
        for key, widget in self._input_widgets.items():
            value_str = widget.text()
            value = self._inputs[key].convert_from_string(value_str)
            result[key] = value
        return result