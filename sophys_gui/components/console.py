import time

from qtpy.QtCore import QCoreApplication, Qt, QObject, Signal, Slot, QUrl, QThread
from qtpy.QtGui import QTextOption, QColor
from qtpy.QtWidgets import QTextEdit, QScrollArea

from bluesky_queueserver_api.comm_base import RequestTimeoutError
from bluesky_queueserver_api.console_monitor import _ConsoleMonitor as ConsoleMonitor


class ConsolePollingWorker(QObject):
    new_message_received = Signal(str, str)  # timestamp, msg

    @staticmethod
    def create(thread: QThread, console_monitor: ConsoleMonitor):
        polling_worker = ConsolePollingWorker(console_monitor)
        polling_worker.moveToThread(thread)

        thread.started.connect(polling_worker.run)
        thread.finished.connect(polling_worker.deleteLater)

        return polling_worker

    def __init__(self, console_monitor: ConsoleMonitor):
        super().__init__()

        self._console_monitor = console_monitor
        self._last_text_uid = None

    @Slot()
    def run(self):
        old_max_lines = self._console_monitor.text_max_lines

        self._console_monitor.text_max_lines = 0
        self._console_monitor.enable()

        current_thread = QThread.currentThread()
        while not current_thread.isInterruptionRequested():
            if self._console_monitor.text_uid == self._last_text_uid:
                time.sleep(0.1)

                continue

            self._last_text_uid = self._console_monitor.text_uid

            msgs = list()
            while True:
                try:
                    msgs.append(self._console_monitor.next_msg(timeout=0))
                except RequestTimeoutError:
                    break

            for msg in msgs:
                self.new_message_received.emit("", msg)

        self._console_monitor.disable()
        self._console_monitor.text_max_lines = old_max_lines

        current_thread.quit()


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

    def __init__(self, model, all_logs=False):
        super().__init__()
        self.all_logs = all_logs
        self.run_engine = model.run_engine

        self._setupUi()

        self._worker_thread = QThread()

        self._worker = ConsolePollingWorker.create(self._worker_thread, self.run_engine._client._console_monitor)
        self._worker.new_message_received.connect(lambda _, msg: self.onAppendLine(msg))

        self._worker_thread.start()

        QCoreApplication.instance().aboutToQuit.connect(self.exit)

    @Slot(str)
    def onAppendLine(self, line: str):
        if "bluesky_queueserver" in line:
            self.console.setTextColor(QColor("#2f00ff"))
        elif "[E " in line:
            self.console.setTextColor(QColor("#cc0000"))
        elif "[W " in line:
            self.console.setTextColor(QColor("#cc9900"))
        elif "[I " in line:
            if "run_engine" in line:
                self.console.setTextColor(QColor("#2f00ff"))
            else:
                self.console.setTextColor(QColor("#00501B"))
        elif "[D " in line:
            self.console.setTextColor(QColor("#007A99"))
        else:
            self.console.setTextColor(QColor("#000000"))
        self.console.append(line)
        self.scrollBar.setValue(self.scrollBar.maximum())

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

    def exit(self):
        self._worker_thread.requestInterruption()
        self._worker_thread.wait()
