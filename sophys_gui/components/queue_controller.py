import qtawesome as qta
from qtpy.QtWidgets import QWidget, QHBoxLayout, QGroupBox, \
    QStackedWidget, QPushButton
from .led import SophysLed


class QueueController(QWidget):

    def __init__(self, model):
        super().__init__()
        self.serverModel = model
        self.updateEvent = self.serverModel.run_engine.events.status_changed
        self.statusVar = self.serverModel.run_engine.re_manager_status
        self.setMaximumHeight(75)
        self._setupUi()

    def statusChanged(self, evt):
        statusVal = self.statusVar.get('re_state', None)
        currIndex = 0 if statusVal == 'idle' else 1 if statusVal == 'running' else 2
        self.play_stack.setCurrentIndex(currIndex)
        self.stop_stack.setCurrentIndex(currIndex)

    def addStatusGroup(self, title, param_dict):
        group = QGroupBox()
        group.setTitle(title)
        groupLay = QHBoxLayout()
        group.setLayout(groupLay)

        statusKey = param_dict["key"]
        statusComp = param_dict["comp"]
        isConn = 'conn' in param_dict
        led = SophysLed(
            self.updateEvent, self.statusVar, statusKey,
            statusComp, isConn)
        groupLay.addWidget(led)
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
                'comp': lambda boolVar: boolVar
            },
            'Running': {
                'key': 're_state',
                'comp': lambda stateVar: stateVar=="running"
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
            btn.clicked.connect(btn_stack["cmd"])
            if 'enabled' in btn_stack:
                btn.setEnabled(False)
            stack.addWidget(btn)

        return stack

    def addPlayController(self, hlay):
        cmd_start = [
            {
                'icon': 'fa5s.play',
                'title': 'Start',
                'cmd': self.serverModel.run_engine.queue_start
            },
            {
                'icon': 'fa5s.pause',
                'title': 'Pause',
                'cmd': lambda _: self.serverModel.run_engine.re_pause(option='deferred')
            },
            {
                'icon': 'fa5s.play',
                'title': 'Resume',
                'cmd': self.serverModel.run_engine.re_resume
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
                'enabled': False
            },
            {
                'icon': 'fa5s.stop',
                'title': 'Stop',
                'cmd': self.serverModel.run_engine.queue_stop
            },
            {
                'icon': 'fa5s.stop',
                'title': 'Abort',
                'cmd': self.serverModel.run_engine.re_abort
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

        group = self.addControllerGroup()
        group.setMinimumWidth(300)
        hlay.addWidget(group)

        self.addStatusLeds(hlay)

        self.updateEvent.connect(self.statusChanged)
