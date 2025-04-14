from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QProgressBar
from sophys_gui.server import KafkaDataRegister


class ProgressBar(QProgressBar):
    """
        Widget that displays the progress of the current plan.
    """

    def __init__(self, run_engine, kafka_bootstrap, kafka_topic):
        super().__init__()
        self.run_engine = run_engine
        self.kafka_monitor = KafkaDataRegister(kafka_bootstrap, kafka_topic)
        self.kafka_timer = QTimer()
        self.kafka_timer.setInterval(150)
        self.kafka_timer.timeout.connect(self.kafka_monitor_callback)
        self.run_engine.events.running_item_changed.connect(self.runningItemChanged)

    def runningItemChanged(self, evt):
        runningItem = self.run_engine._running_item
        hasRunningItem = len(runningItem) != 0
        if hasRunningItem:
            print("3")
            # self.kafka_monitor.clear_data()
            # self.kafka_timer.start()

    def kafka_monitor_callback(self):
        print("1")