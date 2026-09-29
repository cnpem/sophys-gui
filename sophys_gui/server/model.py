from collections.abc import Callable
from functools import partial
import threading
import time as ttime

from bluesky_queueserver_api import WaitMonitor
from bluesky_widgets.models.run_engine_client import RunEngineClient
from qtpy.QtCore import Q_ARG, QCoreApplication, QMetaObject, QObject, QThread, Slot


def is_main_thread(thread: QThread) -> bool:
    instance = QCoreApplication.instance()
    assert instance is not None, "No QCoreApplication running."
    return thread is instance.thread()


class MonitorConditionWorker(QObject):
    @staticmethod
    def create(thread: QThread, parent: QObject, run_engine: RunEngineClient):
        worker = MonitorConditionWorker(parent, run_engine)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        thread.finished.connect(worker.deleteLater)

        return worker

    def __init__(self, parent: QObject, run_engine: RunEngineClient):
        super().__init__()

        assert hasattr(parent, "run_in_main_thread")
        self._parent = parent
        self._run_engine = run_engine

        self._conditions = list()
        self._failed_conditions = set()
        self._executing_conditions = set()

        self._threads = list()

        self._main_thread = QThread.currentThread()

    def add_condition(self, condition: Callable, on_change: Callable):
        self._conditions.append((condition, on_change))
        self.stop_current_processing()

    def stop_current_processing(self):
        for _, monitor in self._executing_conditions:
            monitor.cancel()

    @Slot()
    def run(self):
        current_thread = QThread.currentThread()
        while not current_thread.isInterruptionRequested():
            self._threads = [_t for _t in self._threads if _t.is_alive()]

            for condition, on_change in self._conditions:
                if condition in self._failed_conditions:
                    continue
                if condition in self._executing_conditions:
                    continue

                monitor = WaitMonitor()

                thread = threading.Thread(target=self._run_with_monitor, args=(monitor, condition, on_change))
                self._threads.append(thread)

                self._executing_conditions.add((condition, monitor))

                thread.start()

            while all(_t.is_alive() for _t in self._threads):
                ttime.sleep(0.4)
                for thread in self._threads:
                    thread.join(timeout=0.2)

        current_thread.quit()

    def _run_with_monitor(self, monitor: WaitMonitor, condition: Callable, on_change: Callable):
        try:
            client = self._run_engine._client

            try:
                client.wait_for_condition(condition, timeout=10, monitor=monitor)
            except (client.WaitCancelError, client.WaitTimeoutError):
                pass
            else:
                QMetaObject.invokeMethod(self._parent, "run_in_main_thread", Q_ARG(object, on_change))

                self._executing_conditions.remove((condition, monitor))
        except Exception:
            self._failed_conditions.add(condition)

            raise


class ServerModel(QObject):
    """
        Class for monitoring and communicating with the Bluesky Run Engine.
    """

    def __init__(self, http_server_uri: str, api_key: str | None = None):
        super().__init__()

        self.run_engine = RunEngineClient(
            http_server_uri=http_server_uri,
            http_server_api_key=api_key
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
                status["status_uid"] != self.run_engine.re_manager_status.get("status_uid", "")
            ),
            partial(self.run_engine.load_re_manager_status, unbuffered=True),
        )
        self._worker_thread.start()

        if (instance := QCoreApplication.instance()) is not None:
            instance.aboutToQuit.connect(self.exit)

    @Slot(object)
    def run_in_main_thread(self, functor: Callable, *args, **kwargs):
        assert is_main_thread(QThread.currentThread())

        functor(*args, **kwargs)

    def exit(self):
        self._worker_thread.requestInterruption()
        self._condition_monitor.stop_current_processing()
        self._worker_thread.wait()
