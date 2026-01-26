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
        self.event_sum = 0
        self.last_run = 0
        self.multi_run = False
        self.setMaximum(100)
        self.setMinimum(0)
        self.metadata = {}
        self.kafka_monitor = KafkaDataRegister(kafka_bootstrap, kafka_topic)
        self.kafka_timer = QTimer()
        self.kafka_timer.setInterval(150)
        self.kafka_timer.timeout.connect(self.kafka_monitor_callback)
        self.run_engine.events.running_item_changed.connect(self.runningItemChanged)

    @DeferredFunction
    def handle_plan_args(self, runningItem):
        self.total_events = self.metadata.get("total_seq_num", 1)

        kwargs = runningItem["kwargs"]
        isGrid = "grid" in runningItem["name"]
        isList = "list" in runningItem["name"]
       
        if "metadata" in kwargs:
            if "total_seq_num" in kwargs["metadata"]:
                self.total_events = int(kwargs["metadata"]["total_seq_num"])
                self.multi_run = True
                return
            
        if "num" in kwargs:
            self.total_events = kwargs["num"]
        elif "args" in kwargs:
            motor_args = kwargs["args"]
            if isGrid:
                for num, arg in enumerate(motor_args):
                    if isinstance(arg, list):
                        self.total_events *= len(arg)
                    elif not isList and (num+1)%4 == 0:
                        self.total_events *= arg
            elif isList:
                args_size = len(motor_args[1])
                if args_size > 0:
                    self.total_events = args_size

    @DeferredFunction
    def runningItemChanged(self, evt):
        runningItem = self.run_engine._running_item
        hasRunningItem = len(runningItem) != 0
        if hasRunningItem:
            self.handle_plan_args(runningItem)
            self.kafka_timer.start()
            self.setVisible(True)
        else:
            self.kafka_timer.stop()
            self.setVisible(False)
            self.setValue(0)
            self.multi_run = False
            self.last_run = 0
            self.event_sum = 0
            self.kafka_monitor.get_data()

    @DeferredFunction
    def kafka_monitor_callback(self):
        kafka_data = self.kafka_monitor.get_data()
        events_size = len(kafka_data)

        if events_size > 0:
            if "total_seq_num" in kafka_data[0]:
                self.metadata = kafka_data[0]
                self.total_events = int(self.metadata.get("total_seq_num", 1))
                self.multi_run = True

            last_run = kafka_data[-1]
            seq_num = 0
            if "seq_num" in last_run:
                if self.multi_run:
                    if last_run["seq_num"] > self.last_run:
                        self.event_sum += last_run["seq_num"] - self.last_run
                    else:
                        self.event_sum += last_run["seq_num"]
                    seq_num = self.event_sum
                    self.last_run = last_run["seq_num"]
                else:
                    seq_num = last_run["seq_num"]
                self.setValue(int(100*seq_num/self.total_events))