from collections.abc import Generator

from bluesky_queueserver_api.comm_threads import ReManagerComm_HTTP_Threads
import pytest
from qtpy.QtCore import QThread

from sophys_gui.components.console import ConsolePollingWorker, SophysConsoleMonitor

CONSOLE_MESSAGES = ({"timestamp": 0, "msg": "[E ] This is message #1."}, {"timestamp": 1, "msg": "[D ] This is message #2."}, {"timestamp": 2, "msg": "[I ] This is message #3."})


class DummyReManagerComm(ReManagerComm_HTTP_Threads):
    def __init__(self):
        super().__init__(http_server_uri="http://test", console_monitor_poll_period=0.1)

    def get_console_monitor(self):
        return self._console_monitor


@pytest.fixture
def mock_with_console_lines(httpx_mock):
    for response_message in CONSOLE_MESSAGES:
        httpx_mock.add_response(
            url="http://test/api/console_output_update",
            json={
                "console_output_msgs": [response_message],
                "last_msg_uid": hash(response_message["msg"]),
            },
        )

    yield

    # NOTE: Only printed in debug settings (-s or failed test)
    print(httpx_mock.get_requests())


@pytest.fixture
def mock_console_worker() -> Generator[tuple[ConsolePollingWorker, QThread], None, None]:
    _comm = DummyReManagerComm()
    console_monitor = _comm.get_console_monitor()
    worker_thread = QThread()

    console_worker = ConsolePollingWorker.create(worker_thread, console_monitor)

    yield console_worker, worker_thread

    worker_thread.requestInterruption()
    worker_thread.wait(1_000)


@pytest.mark.httpx_mock(assert_all_requests_were_expected=False)
def test_polling_worker(qtbot, mock_with_console_lines, mock_console_worker):
    console_worker, worker_thread = mock_console_worker

    with qtbot.waitSignals([console_worker.new_message_received] * 3, timeout=1_000, raising=False) as blocker:
        blocker._timer.timeout.connect(worker_thread.requestInterruption)

        worker_thread.start()

    assert blocker.signal_triggered, blocker._timeout_message

    for signal, expected_message in zip(blocker.all_signals_and_args, CONSOLE_MESSAGES, strict=False):
        assert signal.args[1] == expected_message["msg"]


@pytest.mark.httpx_mock(assert_all_requests_were_expected=False)
def test_console_log_level_filter(qtbot, mock_with_console_lines, mock_console_worker):
    console_worker, worker_thread = mock_console_worker

    partial_logs_console_widget = SophysConsoleMonitor(all_logs=False, mock_worker=console_worker)
    full_logs_console_widget = SophysConsoleMonitor(all_logs=True, mock_worker=console_worker)

    with qtbot.waitSignals([console_worker.new_message_received] * 3, timeout=1_000, raising=False) as blocker:
        blocker._timer.timeout.connect(worker_thread.requestInterruption)

        worker_thread.start()

    assert blocker.signal_triggered, blocker._timeout_message

    partial_logs = partial_logs_console_widget.console.toPlainText()
    assert len(partial_logs.split("\n")) == 2

    full_logs = full_logs_console_widget.console.toPlainText()
    assert len(full_logs.split("\n")) == 3
