from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, \
    QSlider


class SophysSwitchButton(QWidget):

    def __init__(self: QWidget, title: str, command: object) -> None:
        super().__init__()
        self.title = title
        self.cmd = command
        self.setupUi()

    def set_slider_style(self: QWidget, slider: QSlider) -> None:
        """
            Set the style of the switch widget.
        """
        slider.setStyleSheet(
            """
                QSlider{
                    background: #00000000;
                    border-radius: 5px;
                }
                QSlider::sub-page {
                    background: #00cc00;
                    border: 1px solid #777;
                    border-radius: 5px;
                }
                QSlider::add-page {
                    background: #1c6f0d;
                    border: 1px solid #777;
                    border-radius: 5px;
                }
                QSlider::handle {
                    background: #ffffff;
                    border: 1px solid #777;
                    width: 13px;
                    border-radius: 5px;
                }
            """
        )

    def set_slider_parameters(self: QWidget, slider: QSlider) -> None:
        """
            Set slider default parameters for it to become a switch.
        """
        slider.setMinimum(0)
        slider.setMaximum(1)
        slider.setTickInterval = 1
        slider.valueChanged.connect(self.cmd)

    def build_slider(self: QWidget) -> QSlider:
        """
            Create a slider widget and configure it.
        """
        slider = QSlider(Qt.Horizontal)
        self.set_slider_style(slider)
        self.set_slider_parameters(slider)
        slider.setMaximumHeight(50)
        return slider

    def add_title(self, lay: QGridLayout) -> None:
        upper_limit = QLabel(self.title)
        upper_limit.setAlignment(Qt.AlignCenter|Qt.AlignBottom)
        lay.addWidget(upper_limit, 0, 0, 1, 2)


    def add_lower_and_higher_labels(self: QWidget, lay: QGridLayout) -> None:
        """
            Add labels for both sides of the switch.
        """
        lower_limit = QLabel("Off")
        lower_limit.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        lay.addWidget(lower_limit, 2, 0, 1, 1)

        upper_limit = QLabel("On")
        upper_limit.setAlignment(Qt.AlignRight|Qt.AlignTop)
        lay.addWidget(upper_limit, 2, 1, 1, 1)

    def setupUi(self: QWidget) -> None:
        """
            Create and group the slider and labels.
        """
        glay = QGridLayout()

        wid = QWidget()
        slide_lay = QGridLayout()
        wid.setLayout(slide_lay)

        wid.setMaximumWidth(50)
        slide_lay.setContentsMargins(0, 0, 0, 0)
        slide_lay.setSpacing(0)

        self.slider = self.build_slider()
        self.add_title(slide_lay)
        self.add_lower_and_higher_labels(slide_lay)
        slide_lay.addWidget(self.slider, 1, 0, 1, 2)

        glay.addWidget(wid)
        self.setLayout(glay)
