import qtawesome as qta
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QWidget, QHBoxLayout, QGroupBox, \
    QStackedWidget, QPushButton
from .led import SophysLed


class QueueController(QWidget):

    def __init__(self, model):
        super().__init__()
        self.run_engine = model.run_engine
        self.updateEvent = self.run_engine.events.status_changed
        self.statusVar = self.run_engine.re_manager_status
        self.setMaximumHeight(75)
        self._setupUi()

    def statusChanged(self, evt):
        if evt.is_connected:
            envVal = self.statusVar.get('worker_environment_exists', None)
            statusVal = self.statusVar.get('manager_state', None)
            currIndex = 0 if statusVal == 'idle' else 1 if statusVal == 'executing_queue' else 2
            self.play_stack.setCurrentIndex(currIndex)
            self.play_stack.setEnabled(envVal)
            self.stop_stack.setCurrentIndex(currIndex)
            self.stop_stack.setEnabled(envVal)

            currIndex = 1 if envVal else 0
            self.env_stack.setCurrentIndex(currIndex)

    def addStatusGroup(self, title, param_dict):
        group = QGroupBox()
        group.setTitle(title)
        groupLay = QHBoxLayout()
        groupLay.setContentsMargins(25, 2, 25, 2)
        group.setLayout(groupLay)

        if 'control' in param_dict:
            self.addEnvironmentController(groupLay)

        statusKey = param_dict["key"]
        statusComp = param_dict["comp"]
        isConn = 'conn' in param_dict
        led = SophysLed(
            self.updateEvent, self.statusVar, statusKey,
            statusComp, isConn)
        groupLay.addWidget(led)

        if 'loading' in param_dict:
            loadingKey = param_dict["loading"]["key"]
            loadingComp = param_dict["loading"]["comp"]
            loading = SophysLed(
                self.updateEvent, self.statusVar, loadingKey,
                loadingComp, isLoading=True)
            groupLay.addWidget(loading)

        return group

    def addStatusLeds(self, hlay):
        status_leds = {
            'Connected': {
                'key': 'worker_environment_exists',
                'comp': True,
                'conn': True
            },
            'Environment': {
                'key': 'worker_environment_exists',
                'comp': lambda boolVar: boolVar,
                'control': self.run_engine.environment_open,
                'loading': {
                    'key': 'manager_state',
                    'comp': lambda stateVar:
                        stateVar=="creating_environment" or stateVar=="closing_environment"
                }
            },
            'Running': {
                'key': 'manager_state',
                'comp': lambda stateVar: stateVar == "executing_queue"
            },
            'Stop Pending': {
                'key': 'queue_stop_pending',
                'comp': lambda boolVar: boolVar
            }
        }

        for title, param_dict in status_leds.items():
            ledGroup = self.addStatusGroup(title, param_dict)
            hlay.addWidget(ledGroup)

    def addQueueController(self, cmd_btn_dict):
        stack = QStackedWidget()
        for btn_stack in cmd_btn_dict:
            btn = QPushButton(btn_stack["title"])
            btn.setIcon(qta.icon(btn_stack["icon"]))
            btn.setIconSize(QSize(20, 20))
            btn.clicked.connect(btn_stack["cmd"])
            btn.setToolTip(btn_stack["tooltip"])
            if 'enabled' in btn_stack:
                btn.setEnabled(False)
            stack.addWidget(btn)

        return stack

    def addEnvironmentController(self, hlay):
        cmd_env = [
            {
                'icon': 'mdi6.progress-check',
                'title': 'Open',
                'cmd': self.run_engine.environment_open,
                "tooltip": "Open the Bluesky Environment."
            },
            {
                'icon': 'mdi6.progress-close',
                'title': 'Close',
                'cmd': self.run_engine.environment_close,
                "tooltip": "Close the Bluesky Environment."
            }
        ]
        self.env_stack = self.addQueueController(cmd_env)
        hlay.addWidget(self.env_stack)

    def addPlayController(self, hlay):
        cmd_start = [
            {
                'icon': 'fa5s.play',
                'title': 'Start',
                'cmd': self.run_engine.queue_start,
                "tooltip": "Start running the first queue item."
            },
            {
                'icon': 'fa5s.pause',
                'title': 'Pause',
                'cmd': lambda _: self.run_engine.re_pause(option='deferred'),
                "tooltip": "Pause the running item."
            },
            {
                'icon': 'fa5s.play',
                'title': 'Resume',
                'cmd': self.run_engine.re_resume,
                "tooltip": "Resume running the paused queue item."
            }
        ]
        self.play_stack = self.addQueueController(cmd_start)
        hlay.addWidget(self.play_stack)

    def addStopController(self, hlay):
        cmd_start = [
            {
                'icon': 'fa5s.stop',
                'title': 'Stop',
                'cmd': print,
                'enabled': False,
                "tooltip": "Stop running the queue list."
            },
            {
                'icon': 'fa5s.stop',
                'title': 'Stop',
                'cmd': self.run_engine.queue_stop,
                "tooltip": "Stop running the queue list."
            },
            {
                'icon': 'fa5s.stop',
                'title': 'Abort',
                'cmd': self.run_engine.re_abort,
                "tooltip": "Cancel running the paused item. This will item will " \
                    "show in the history with the aborted status."
            }
        ]
        self.stop_stack = self.addQueueController(cmd_start)
        hlay.addWidget(self.stop_stack)

    def addControllerGroup(self):
        group = QGroupBox()
        hlay = QHBoxLayout()
        group.setLayout(hlay)
        group.setTitle("Queue Controller")
        hlay.setContentsMargins(25, 2, 25, 2)

        self.addPlayController(hlay)
        self.addStopController(hlay)

        return group

    def _setupUi(self):
        hlay = QHBoxLayout(self)

        self.addStatusLeds(hlay)

        group = self.addControllerGroup()
        group.setMinimumWidth(300)
        hlay.addWidget(group)


        self.updateEvent.connect(self.statusChanged)
