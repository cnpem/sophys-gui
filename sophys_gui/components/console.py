from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QScrollArea
from suitscase.utilities.threading import AsyncFunction, \
    DeferredFunction


class SophysConsoleMonitor(QScrollArea):

    def __init__(self, model):
        super().__init__()
        self.run_engine = model.run_engine
        self.consoleOutputs = ""
        self.console = QLabel("")

        self._setupUi()
        self.serverMonitor()

    @DeferredFunction
    def updateConsoleLabel(self, output):
        if output != "":
            self.consoleOutputs += output + "\n"
            self.console.setText(self.consoleOutputs)

    @AsyncFunction
    def serverMonitor(self):
        """
            Monitor and send new labels for the label widget.
        """
        self.run_engine.start_console_output_monitoring()
        while True:
            newOutput = self.run_engine.console_monitoring_thread()
            if newOutput:
                self.updateConsoleLabel(newOutput[1].strip())
            else:
                break

    def getConsoleLabel(self):
        consoleLbl = QLabel("")
        consoleLbl.setWordWrap(True)
        consoleLbl.setAlignment(Qt.AlignTop)
        consoleLbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        return consoleLbl

    def scrollToBottom(self):
        self.scrollBar.setValue(self.scrollBar.maximum())

    def _setupUi(self):
        self.console = self.getConsoleLabel()
        self.setWidget(self.console)
        self.setWidgetResizable(True)
        self.scrollBar = self.verticalScrollBar()
        self.scrollBar.rangeChanged.connect(self.scrollToBottom)
