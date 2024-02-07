from qtpy.QtWidgets import QStackedWidget, QLabel


class SophysLed(QStackedWidget):

    def __init__(self, updateEvent, statusVar, statusKey, statusComp, isConn=False):
        super().__init__()
        self.updateEvent = updateEvent
        self.statusVar = statusVar
        self.statusKey = statusKey
        self.statusComp = statusComp
        self.isConn = isConn

        self.onColor = ["#00ee00", "#00c700"]
        self.offColor = ["#1c6f0d", "#0f3f07"]

        self.setupUi()

    def updateLoopState(self, evt):
        if self.isConn:
            ledStatus = evt.is_connected
        else:
            status = self.statusVar
            statusVal = status.get(self.statusKey, None)
            ledStatus = self.statusComp(statusVal)
        self.setCurrentIndex(1 if ledStatus else 0)

    def addLed(self, color):
        label = QLabel('')
        label.setStyleSheet("""
            background: qradialgradient(
                cx: 0.5, cy: 0.5, radius: 0.5,
                fx: 0.5, fy: 0.5,
                stop: 0 """+color[0]+""",
                stop: 1 """+color[1]+"""
            );
            border-radius: 9px;
            border: 1px inset #000000;
        """)

        return label

    def setupUi(self):
        self.addWidget(self.addLed(self.offColor))
        self.addWidget(self.addLed(self.onColor))
        self.updateEvent.connect(
            self.updateLoopState)
        self.setFixedSize(20, 20)
