from qtpy.QtWidgets import QWidget, QLabel, QHBoxLayout, \
    QHBoxLayout, QStackedWidget, QCheckBox, QDoubleSpinBox
from sophys_gui.functions import handleSpinboxWidget


class SophysSpinBox(QWidget):
    """
        Spinbox with handlers for 'None' value, int and floats.

        Normal Spinbox:

        .. image:: ./_static/spinbox_val.png
            :width: 500
            :alt: Spinbox Widget
            :align: center

        Spinbox with None value:

        .. image:: ./_static/spinbox_none.png
            :width: 150
            :alt: Spinbox Widget with None value
            :align: center
    """

    def __init__(self, valueType, isRequired = True):
        super().__init__()
        self.value = 0 if isRequired else None
        self.isRequired = isRequired
        self._setupUi(valueType)

    def text(self):
        """
            Return the inserted value as a string.
        """
        return str(self.value)

    def setPlaceholderText(self, value):
        """
            Implement placeholder for default values.
        """
        self.setValue(value)

    def setValue(self, value):
        """
            Add pre-existing value to the widget.
        """
        isNone = value == '' or value == 'None'
        if isNone:
            self.stack.setCurrentIndex(0)
        else:
            self.spinbox.setValue(float(value) if isinstance(self.spinbox, QDoubleSpinBox) else int(value))
            self.stack.setCurrentIndex(1)
            if not self.isRequired:
                self.cb.setChecked(True)
        self.value = value

    def toggleStack(self, value):
        """
            Change stack value between None and a chosen value.
        """
        self.stack.setCurrentIndex(value)
        isNone = value == '' or value == 'None'
        if isNone:
            self.value = ''

    def _setupUi(self, valueType):
        hlay = QHBoxLayout(self)

        self.stack = QStackedWidget()

        if not self.isRequired:
            self.cb = QCheckBox()
            hlay.addWidget(self.cb)
            self.cb.clicked.connect(self.toggleStack)

            noneLbl = QLabel("None")
            self.stack.addWidget(noneLbl)

        self.spinbox = handleSpinboxWidget(valueType)
        self.spinbox.setMinimum(-10000)
        self.spinbox.setMaximum(10000)
        self.stack.addWidget(self.spinbox)
        self.spinbox.setValue(0)

        hlay.addWidget(self.stack)