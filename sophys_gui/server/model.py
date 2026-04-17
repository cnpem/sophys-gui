from functools import partial
import threading
import time

from qtpy.QtCore import QObject, QThread, Slot

from bluesky_queueserver_api import WaitMonitor
from bluesky_widgets.models.run_engine_client import RunEngineClient


class MonitorConditionWorker(QObject):
    @staticmethod
    def create(thread: QThread):
        worker = MonitorConditionWorker()
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        thread.finished.connect(worker.deleteLater)

        return worker

    def __init__(self):
        super().__init__()

        self._conditions = list()

        self._monitors = list()
        self._threads = list()

    def add_condition(self, condition, on_change):
        self._conditions.append((condition, on_change))
        self.stop_current_processing()

    def stop_current_processing(self):
        for monitor in self._monitors:
            monitor.cancel()

    @Slot()
    def run(self):
        current_thread = QThread.currentThread()
        while not current_thread.isInterruptionRequested():
            self._monitors.clear()
            self._threads.clear()

            for condition, on_change in self._conditions:
                monitor = WaitMonitor()
                self._monitors.append(monitor)

                thread = threading.Thread(target=self._run_with_monitor, args=(monitor, condition, on_change))
                self._threads.append(thread)

                thread.start()

            for thread in self._threads:
                thread.join()

    def _run_with_monitor(self, monitor, condition, on_change):
        client = self.run_engine._client

        try:
            client.wait_for_condition(condition, monitor=monitor)
        except (client.WaitCancelError, client.WaitTimeoutError):
            return

        on_change()


class ServerModel:
    """
        Class for monitoring and communicating with the Bluesky Run Engine.
    """

    def __init__(self, http_server_uri, api_key=None):
        """
            Start the Run Engine client and monitor some aspects of it.
        """
        if api_key is not None:
            self.run_engine = RunEngineClient(
                http_server_uri=http_server_uri,
                http_server_api_key=api_key
            )
        else:
            self.run_engine = RunEngineClient(
                http_server_uri=http_server_uri
            )

        # NOTE: Keep a reference to the URI for widgets to use.
        setattr(self.run_engine, "base_uri", http_server_uri)

        self._worker_thread = QThread()
        self._condition_monitor = MonitorConditionWorker.create(self._worker_thread)
        self._condition_monitor.add_condition(
            lambda status: status["plan_queue_uid"] != self.run_engine._plan_queue_uid,
            self.run_engine.manager_connecting_ops,
        )
        self._condition_monitor.add_condition(
            lambda status: (
                status["plan_queue_mode"] != self.run_engine.events.status_changed
            ),
            partial(self.run_engine.load_re_manager_status, unbuffered=True),
        )
        self._worker_thread.start()

    def exit(self):
        """
            Stop monitoring the Run Engine.
        """
        self._worker_thread.requestInterruption()
        self._condition_monitor.stop_current_processing()
        self._worker_thread.wait()

