from functools import partial
import threading

from qtpy.QtCore import QCoreApplication, QObject, QMetaObject, QThread, Slot, Q_ARG

from bluesky_queueserver_api import WaitMonitor
from bluesky_widgets.models.run_engine_client import RunEngineClient



def is_main_thread(thread: QThread) -> bool:
    instance = QCoreApplication.instance()
    assert instance is not None, "No QCoreApplication running."
    return thread is instance.thread()


class MonitorConditionWorker(QObject):
    @staticmethod
    def create(thread: QThread, parent: QObject, run_engine):
        worker = MonitorConditionWorker(parent, run_engine)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        thread.finished.connect(worker.deleteLater)

        return worker

    def __init__(self, parent, run_engine):
        super().__init__()

        assert hasattr(parent, "run_in_main_thread")
        self._parent = parent
        self._run_engine = run_engine

        self._conditions = list()
        self._failed_conditions = set()

        self._monitors = list()
        self._threads = list()

        self._main_thread = QThread.currentThread()

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
                if condition in self._failed_conditions:
                    continue

                monitor = WaitMonitor()
                self._monitors.append(monitor)

                thread = threading.Thread(target=self._run_with_monitor, args=(monitor, condition, on_change))
                self._threads.append(thread)

                thread.start()

            for thread in self._threads:
                thread.join()

        current_thread.quit()

    def _run_with_monitor(self, monitor, condition, on_change):
        try:
            client = self._run_engine._client

            try:
                client.wait_for_condition(condition, monitor=monitor)
            except (client.WaitCancelError, client.WaitTimeoutError):
                pass
            else:
                QMetaObject.invokeMethod(self._parent, "run_in_main_thread", Q_ARG(object, on_change))
        except Exception:
            self._failed_conditions.add(condition)

            raise


class ServerModel(QObject):
    """
        Class for monitoring and communicating with the Bluesky Run Engine.
    """

    def __init__(self, http_server_uri, api_key=None):
        super().__init__()

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
        self._condition_monitor = MonitorConditionWorker.create(self._worker_thread, self, self.run_engine)
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

        QCoreApplication.instance().aboutToQuit.connect(self.exit)

    @Slot(object)
    def run_in_main_thread(self, functor, *args, **kwargs):
        assert is_main_thread(QThread.currentThread())

        functor(*args, **kwargs)

    def exit(self):
        self._worker_thread.requestInterruption()
        self._condition_monitor.stop_current_processing()
        self._worker_thread.wait()
