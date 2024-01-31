import os
import sys
import time

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

        self.monitor_queue_changes()

    def exit(self):
        self.__queue_monitor.cancel()
        while self.__monitoring_queue:
            time.sleep(0.01)

    @AsyncFunction
    def monitor_queue_changes(self):
        self.__monitoring_queue = True
        self.__queue_monitor = WaitMonitor()
        while True:
            self.__queue_uid = self.run_engine._plan_queue_uid
            try:
                self.run_engine._client.wait_for_condition(lambda status: status["plan_queue_uid"] != self.__queue_uid, timeout=sys.float_info.max, monitor=self.__queue_monitor)
            except self.run_engine._client.WaitCancelError:
                break
            except self.run_engine._client.WaitTimeoutError:
                pass
            self.run_engine.load_plan_queue()
        self.__monitoring_queue = False
