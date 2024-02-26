from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QScrollArea
from suitscase.utilities.threading import AsyncFunction, \
    DeferredFunction


class SophysConsoleMonitor(QScrollArea):

    def __init__(self, model):
        super().__init__()
        self.run_engine = model.run_engine
        self.consoleOutputs = ""

        self._setupUi()
        self.server_monitor()

    @DeferredFunction
    def updateConsoleLabel(self, output):
        if output != "":
            self.consoleOutputs += output + "\n"
            self.console.setText(self.consoleOutputs)

    @AsyncFunction
    def server_monitor(self):
        self.run_engine.start_console_output_monitoring()
        while True:
            newOutput = self.run_engine.console_monitoring_thread()
            self.updateConsoleLabel(newOutput[1].strip())

    def _setupUi(self):
        self.console = QLabel("")
        self.console.setWordWrap(True)
        self.console.setAlignment(Qt.AlignTop)
        self.console.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.setWidgetResizable(True)
        self.setWidget(self.console)
        self.scrollBar = self.verticalScrollBar()
        self.scrollBar.rangeChanged.connect(self.scrollToBottom)

    def scrollToBottom(self):
        self.scrollBar.setValue(self.scrollBar.maximum())
