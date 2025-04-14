from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QProgressBar
from sophys_gui.server import KafkaDataRegister
from suitscase.utilities.threading import DeferredFunction


class ProgressBar(QProgressBar):
    """
        Widget that displays the progress of the current plan.
    """

    def __init__(self, run_engine, kafka_bootstrap, kafka_topic):
        super().__init__()
        self.run_engine = run_engine
        self.total_events = 1
        self.setMaximum(100)
        self.setMinimum(0)
        self.kafka_monitor = KafkaDataRegister(kafka_bootstrap, kafka_topic)
        self.kafka_timer = QTimer()
        self.kafka_timer.setInterval(150)
        self.kafka_timer.timeout.connect(self.kafka_monitor_callback)
        self.run_engine.events.running_item_changed.connect(self.runningItemChanged)

    @DeferredFunction
    def handle_plan_args(self, runningItem):
        if "num" in runningItem["kwargs"]:
            self.total_events = runningItem["kwargs"]["num"]
        elif "args" in runningItem["kwargs"]:
            motor_args = runningItem["kwargs"]["args"][1]
            if len(motor_args) > 0:
                self.total_events = len(motor_args)

    @DeferredFunction
    def runningItemChanged(self, evt):
        runningItem = self.run_engine._running_item
        hasRunningItem = len(runningItem) != 0
        if hasRunningItem:
            self.handle_plan_args(runningItem)
            self.kafka_timer.start()
        else:
            self.kafka_timer.stop()
            self.total_events = 1

    @DeferredFunction
    def kafka_monitor_callback(self):
        events_size = len(self.kafka_monitor.get_data())
        if events_size > 0:
            last_run = self.kafka_monitor.get_data()[-1]
            if "seq_num" in last_run:
                print(self.total_events, last_run["seq_num"])
                self.setValue(int(100*last_run["seq_num"]/self.total_events))
                self.kafka_monitor.clear_data()