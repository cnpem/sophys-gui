import logging
import time

from bluesky_queueserver_api.comm_base import RequestTimeoutError
from bluesky_queueserver_api.console_monitor import _ConsoleMonitor as ConsoleMonitor
from qtpy.QtCore import QCoreApplication, QObject, Qt, QThread, Signal, Slot
from qtpy.QtGui import QColor, QTextOption
from qtpy.QtWidgets import QScrollArea, QTextEdit

from ..server import ServerModel

logger = logging.getLogger("sophys.gui.console")


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

    @Slot()
    def run(self):
        old_max_lines = self._console_monitor.text_max_lines

        self._console_monitor.text_max_lines = 0
        self._console_monitor.enable()

        logger.debug("Console monitoring has started.")

        current_thread = QThread.currentThread()
        while not current_thread.isInterruptionRequested():
            msgs = list()
            while True:
                try:
                    msgs.append(self._console_monitor.next_msg(timeout=0))
                except RequestTimeoutError:
                    break

            for msg in msgs:
                logger.debug("New message has been received.")
                self.new_message_received.emit(str(msg.get("timestamp")), msg.get("msg", ""))

            if len(msgs) == 0:
                time.sleep(0.1)

        logger.debug("Console monitoring has ended.")

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

    def __init__(self, model: ServerModel | None = None, all_logs: bool = False, *, mock_worker: ConsolePollingWorker | None = None):
        super().__init__()

        self._setupUi()

        self._logging_level = logging.DEBUG if all_logs else logging.INFO

        if model is not None:
            self.run_engine = model.run_engine

        if mock_worker is None:
            self._worker_thread = QThread()

            self._worker = ConsolePollingWorker.create(self._worker_thread, self.run_engine._client._console_monitor)
            self._worker.new_message_received.connect(lambda _, msg: self.onAppendLine(msg))

            self._worker_thread.start()

            QCoreApplication.instance().aboutToQuit.connect(self.exit)
        else:
            assert model is None, "Cannot set 'model' while using a mocked console worker."

            self._worker = mock_worker
            self._worker.new_message_received.connect(lambda _, msg: self.onAppendLine(msg))


    def _configure_cursor_for_console_line(self, line: str) -> bool:
        """
        Configure the console widget's current cursor for the next line of text.

        Returns
        -------
        bool
            Indicates whether the current line should be appended to the console text.
        """
        line = line.strip()

        if line.startswith("[E "):
            if self._logging_level > logging.ERROR:
                return False

            self.console.setTextColor(QColor("#cc0000"))
        elif line.startswith("[W "):
            if self._logging_level > logging.WARNING:
                return False

            self.console.setTextColor(QColor("#cc9900"))
        elif line.startswith("[I "):
            if self._logging_level > logging.INFO:
                return False

            if "run_engine" in line:
                self.console.setTextColor(QColor("#2f00ff"))
            else:
                self.console.setTextColor(QColor("#00501B"))
        elif line.startswith("[D "):
            if self._logging_level > logging.DEBUG:
                return False

            self.console.setTextColor(QColor("#007A99"))
        elif "bluesky_queueserver" in line:
            self.console.setTextColor(QColor("#2f00ff"))
        else:
            self.console.setTextColor(QColor("#000000"))

        return True

    @Slot(str)
    def onAppendLine(self, line: str):
        if not self._configure_cursor_for_console_line(line):
            return

        self.console.append(line.strip())
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
