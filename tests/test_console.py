import pytest

from qtpy.QtCore import QThread

from bluesky_queueserver_api.comm_threads import ReManagerComm_HTTP_Threads

from sophys_gui.components.console import ConsolePollingWorker


CONSOLE_MESSAGES = ("This is message #1.", "This is message #2.", "This is message #3.")


class DummyReManagerComm(ReManagerComm_HTTP_Threads):
    def __init__(self):
        super().__init__(http_server_uri="https://localhost", console_monitor_poll_period=0.1)

    def get_console_monitor(self):
        return self._console_monitor


@pytest.mark.httpx_mock(assert_all_requests_were_expected=False)
def test_polling_worker(qtbot, httpx_mock):
    for response_message in CONSOLE_MESSAGES:
        httpx_mock.add_response(
            url="https://localhost/api/console_output_update",
            json={
                "console_output_msgs": [response_message],
                "last_msg_uid": hash(response_message),
            },
        )

    _comm = DummyReManagerComm()
    console_monitor = _comm.get_console_monitor()
    worker_thread = QThread()

    console_worker = ConsolePollingWorker.create(worker_thread, console_monitor)

    with qtbot.waitSignals([console_worker.new_message_received] * 3, timeout=1_000, raising=False) as blocker:
        blocker._timer.timeout.connect(worker_thread.requestInterruption)

        worker_thread.start()

    assert blocker.signal_triggered, blocker._timeout_message
    for signal, expected_message in zip(blocker.all_signals_and_args, CONSOLE_MESSAGES):
        assert signal.args[1] == expected_message

    worker_thread.requestInterruption()
    worker_thread.wait(1_000)

    print(httpx_mock.get_requests())
    
