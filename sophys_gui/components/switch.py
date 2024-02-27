from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QGridLayout, \
    QSlider, QPushButton


class SophysSwitchButton(QPushButton):

    def __init__(self: QPushButton, title: str, command: object, state: int) -> None:
        super().__init__()
        self.title = title
        self.cmd = command
        self.state = bool(state)
        self.setFlat(True)
        self.setupUi()

    def set_slider_parameters(self: QPushButton, slider: QSlider) -> None:
        """
            Set slider default parameters for it to become a switch.
        """
        slider.setMinimum(0)
        slider.setMaximum(1)
        slider.setTickInterval = 1
        slider.setValue(self.state)
        slider.setEnabled(False)

    def build_slider(self: QPushButton) -> QSlider:
        """
            Create a slider widget and configure it.
        """
        slider = QSlider(Qt.Horizontal)
        self.set_slider_parameters(slider)
        slider.setMaximumHeight(50)
        return slider

    def add_title(self, lay: QGridLayout) -> None:
        upper_limit = QLabel(self.title)
        upper_limit.setAlignment(Qt.AlignCenter|Qt.AlignBottom)
        lay.addWidget(upper_limit, 0, 0, 1, 2)


    def add_lower_and_higher_labels(self: QPushButton, lay: QGridLayout) -> None:
        """
            Add labels for both sides of the switch.
        """
        lower_limit = QLabel("Off")
        lower_limit.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        lay.addWidget(lower_limit, 2, 0, 1, 1)

        upper_limit = QLabel("On")
        upper_limit.setAlignment(Qt.AlignRight|Qt.AlignTop)
        lay.addWidget(upper_limit, 2, 1, 1, 1)

    def sendCmd(self):
        self.cmd(not self.state)

    def setupUi(self: QPushButton) -> None:
        """
            Create and group the slider and labels.
        """
        self.setMaximumWidth(65)
        self.setMinimumHeight(40)
        self.setContentsMargins(0, 0, 0, 0)
        self.clicked.connect(self.sendCmd)

        slide_lay = QGridLayout()
        slide_lay.setContentsMargins(0, 0, 0, 0)
        slide_lay.setSpacing(0)

        self.slider = self.build_slider()
        self.add_title(slide_lay)
        self.add_lower_and_higher_labels(slide_lay)
        slide_lay.addWidget(self.slider, 1, 0, 1, 2)

        self.setLayout(slide_lay)
