import time
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QScrollArea
from suitscase.utilities.threading import AsyncFunction, \
    DeferredFunction


class SophysConsoleMonitor(QScrollArea):
    """
        Widget for displaying the Queue Server console logs.

        .. note::
            The console will scroll to the bottom after an update
            in order to show the most recent log.

        .. image:: ./_static/console.png
            :width: 750
            :alt: Console Widget
            :align: center

    """

    def __init__(self, model):
        super().__init__()
        self.run_engine = model.run_engine
        self.consoleOutputs = []
        self.console = QLabel("")

        self._setupUi()
        self.serverMonitor()

    @DeferredFunction
    def updateConsoleLabel(self, output):
        """
            Concatenate the last log to a variable and
            update the label widget.
        """
        if output != "":
            start = time.time()
            self.consoleOutputs.append(output + "\n")
            self.console.setText("".join(self.consoleOutputs))
            end = time.time()
            functDurationMs = end - start
            if functDurationMs > 0.00003:
                self.consoleOutputs = self.consoleOutputs[30:]

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
        """
            Create the label widget.
        """
        consoleLbl = QLabel("")
        consoleLbl.setWordWrap(True)
        consoleLbl.setAlignment(Qt.AlignTop)
        consoleLbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        return consoleLbl

    def scrollToBottom(self):
        """
            Scroll the scroll area to the bottom.
            Used in order to show the latest logs.
        """
        self.scrollBar.setValue(self.scrollBar.maximum())

    def _setupUi(self):
        self.console = self.getConsoleLabel()
        self.setWidget(self.console)
        self.setWidgetResizable(True)
        self.scrollBar = self.verticalScrollBar()
        self.scrollBar.rangeChanged.connect(self.scrollToBottom)
