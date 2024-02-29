from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QTextOption
from qtpy.QtWidgets import QTextEdit, QScrollArea
from suitscase.utilities.threading import AsyncFunction


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

    appendLine = Signal(str)

    def __init__(self, model):
        super().__init__()

        self.run_engine = model.run_engine
        self.appendLine.connect(self.onAppendLine)

        self._setupUi()
        self.serverMonitor()

    @Slot(str)
    def onAppendLine(self, line: str):
        self.console.append(line)
        self.scrollBar.setValue(self.scrollBar.maximum())

    @AsyncFunction
    def serverMonitor(self):
        """
            Monitor and send new labels for the label widget.
        """
        self.run_engine.start_console_output_monitoring()
        while True:
            newOutput = self.run_engine.console_monitoring_thread()
            if newOutput:
                new_console_line = newOutput[1].strip()
                if new_console_line != "":
                    self.appendLine.emit(new_console_line)
            else:
                break

    def getConsoleLabel(self):
        """
            Create the label widget.
        """
        consoleLbl = QTextEdit("", self)
        consoleLbl.setReadOnly(True)
        consoleLbl.setAcceptRichText(False)
        consoleLbl.setWordWrapMode(QTextOption.WordWrap)
        consoleLbl.setAlignment(Qt.AlignTop)
        return consoleLbl

    def _setupUi(self):
        self.console = self.getConsoleLabel()
        self.setWidget(self.console)
        self.setWidgetResizable(True)
        self.scrollBar = self.verticalScrollBar()
