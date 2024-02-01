import os
import sys
import time

from functools import partial
from bluesky_queueserver_api import WaitMonitor
from bluesky_widgets.models.run_engine_client import RunEngineClient

from suitscase.utilities.threading import AsyncFunction


class QueueServerModel:

    def __init__(self):
        http_server_api_key = os.environ.get("QSERVER_HTTP_SERVER_API_KEY", None)

        self.run_engine = RunEngineClient(
            http_server_uri="http://127.0.0.1:http_server_port",
            http_server_api_key=http_server_api_key,
        )

        self.server_callback(
            lambda status: status["plan_queue_uid"] != self.run_engine._plan_queue_uid,
            self.run_engine.load_plan_queue)
        self.server_callback(
            lambda status: status["plan_queue_mode"] != self.run_engine.events.status_changed,
            partial(self.run_engine.load_re_manager_status, unbuffered=True))

    def exit(self):
        self.__queue_monitor.cancel()
        while self.__monitoring_queue:
            time.sleep(0.01)

    @AsyncFunction
    def server_callback(self, param, cmd):
        def monitor_queue_changes():
            self.__monitoring_queue = True
            self.__queue_monitor = WaitMonitor()
            while True:
                try:
                    self.run_engine._client.wait_for_condition(
                        param, timeout=sys.float_info.max, monitor=self.__queue_monitor)
                except self.run_engine._client.WaitCancelError:
                    break
                except self.run_engine._client.WaitTimeoutError:
                    pass
                cmd()
            self.__monitoring_queue = False
        monitor_queue_changes()
