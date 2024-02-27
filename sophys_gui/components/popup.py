import math as _math
from qtpy.QtCore import Qt, QPropertyAnimation, QTimer
from qtpy.QtWidgets import QWidget, QHBoxLayout, \
    QLabel, QGraphicsOpacityEffect


class PopupWidget(QWidget):

    def __init__(self: QWidget, parent: object) -> None:
        super().__init__()
        self.setParent(parent)
        self.setObjectName("popup")
        self._timer = None
        self.setupUi()

    def configure_animation(self: QWidget, anim_type: str) -> None:
        """
            Configure fade in and out animations.
        """
        isFadeIn = (anim_type == 'fadeIn')
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(not isFadeIn)
        self.animation.setEndValue(isFadeIn)
        self.animation.start()

    def fadeout(self: QWidget) -> None:
        """
            Handle popup after timeout.
        """
        self.configure_animation("fadeOut")
        self._timer.stop()
        self.animation.finished.connect(
            lambda: self.setVisible(False))

    def show_popup(self: QWidget) -> None:
        """
            Show the popup widget for a temporary period of time.
        """
        self.setVisible(True)
        self.configure_animation("fadeIn")
        self._timer = QTimer()
        self._timer.timeout.connect(self.fadeout)
        self._timer.setInterval(2000)
        self._timer.start()

    def set_text(self: QWidget, text: str) -> None:
        """
            Change popup label widget.
        """
        self.lbl.setText(text)
        self.setFixedSize(200, 75)

    def get_text_widget(self: QWidget) -> None:
        """
            Create popup label widget.
        """
        self.lbl = QLabel('')
        self.lbl.setWordWrap(True)
        self.lbl.setAlignment(Qt.AlignCenter)

    def create_graphic_effects(self: QWidget) -> None:
        """
            Create graphic effect for animations.
        """
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0)

    def setupUi(self: QWidget) -> None:
        """
            Create the label widget and configure the popup effects.
        """
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.get_text_widget()
        lay.addWidget(self.lbl)

        self.create_graphic_effects()
