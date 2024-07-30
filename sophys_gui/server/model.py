import sys
import time

from functools import partial
from bluesky_queueserver_api import WaitMonitor
from bluesky_widgets.models.run_engine_client import RunEngineClient
from suitscase.utilities.threading import AsyncFunction


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
            
        self.server_callback(
            lambda status: status["plan_queue_uid"] != self.run_engine._plan_queue_uid,
            self.run_engine.manager_connecting_ops)
        self.server_callback(
            lambda status: status["plan_queue_mode"] != self.run_engine.events.status_changed,
            partial(self.run_engine.load_re_manager_status, unbuffered=True))

    def exit(self):
        """
            Stop monitoring the Run Engine.
        """
        self.__server_monitor.cancel()
        while self.__monitoring_server:
            time.sleep(0.01)

    @AsyncFunction
    def server_callback(self, param, cmd):
        """
            Callback function that updates the local Run Engine.
        """
        def monitor_server_changes():
            self.__monitoring_server = True
            self.__server_monitor = WaitMonitor()
            while True:
                try:
                    self.run_engine._client.wait_for_condition(
                        param, timeout=sys.float_info.max, monitor=self.__server_monitor)
                except self.run_engine._client.WaitCancelError:
                    break
                except self.run_engine._client.WaitTimeoutError:
                    pass
                cmd()
            self.__monitoring_server = False
        monitor_server_changes()
