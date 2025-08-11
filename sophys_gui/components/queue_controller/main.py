import qtawesome as qta
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QWidget, QHBoxLayout, QGroupBox, \
    QStackedWidget, QPushButton, QMessageBox
from sophys_gui.functions import addLineJumps
from ..led import SophysLed
from .util import CONFIG


class QueueController(QWidget):
    """
        Widget for controlling and monitoring the Queue Server general parameters.

        .. image:: ./_static/queue_controller.png
            :width: 750
            :alt: Queue Controller Widget
            :align: center

    """

    def __init__(self, run_engine, loginChanged, execution_monitor=False):
        super().__init__()
        self.run_engine = run_engine
        self.updateEvent = self.run_engine.events.status_changed
        self.reStatus = self.run_engine.re_manager_status
        self.isLogged = False
        self.execution_monitor = execution_monitor
        self.cmdStacks = []

        self._setupUi(loginChanged)

    def getRunEngineStatus(self, key):
        return self.reStatus.get(key, None)

    def statusChanged(self, evt):
        """
            Update control buttons based on the Queue Server state.
        """
        isConn = evt.is_connected
        if isConn:
            statusVal = self.getRunEngineStatus("manager_state")
            envVal = self.getRunEngineStatus("worker_environment_exists")
            runIndex = 2 if statusVal == "paused" else 1 if statusVal == "executing_queue" else 0
            for stack in self.cmdStacks[1:]:
                stack.setCurrentIndex(runIndex)
            if self.isLogged:
                self.cmdStacks[1].setEnabled(envVal)
                self.cmdStacks[0].setEnabled(runIndex==0)
            envIndex = 1 if envVal else 0
            self.cmdStacks[0].setCurrentIndex(envIndex)

    def addControlButton(self, btnKey, lay):
        envCmd = CONFIG[btnKey]
        envBtnWid = self.getControllerStack(envCmd)
        self.cmdStacks.append(envBtnWid)
        lay.addWidget(envBtnWid)

    def addStatusLed(self, loadingParams, isConn, isLoading, lay):
        statusKey = loadingParams["key"]
        statusComp = loadingParams["comp"]
        statusLed = SophysLed(
            self.run_engine, statusKey,
            statusComp, isConn, isLoading)
        lay.addWidget(statusLed)

    def addStatusGroup(self, title, param_dict):
        """
            Create a group for monitoring and controling a status element
            of the Queue Server.
        """
        group = QGroupBox()
        group.setTitle(title)
        groupLay = QHBoxLayout()
        groupLay.setContentsMargins(25, 2, 25, 2)
        group.setLayout(groupLay)

        hasControls = "control" in param_dict
        if hasControls:
            self.addControlButton(param_dict["control"], groupLay)

        isConn = "conn" in param_dict
        self.addStatusLed(
            param_dict, isConn, False, groupLay)

        hasLoading = "loading" in param_dict
        if hasLoading:
            self.addStatusLed(
                param_dict["loading"], False, True, groupLay)

        return group

    def addStatusLeds(self, hlay):
        """
            Add leds representing the status of the Queue Server.
        """
        statusLeds = CONFIG["leds"]
        for title, param_dict in statusLeds.items():
            ledGroup = self.addStatusGroup(title, param_dict)
            hlay.addWidget(ledGroup)

    def getSinglePushButton(self, btnConfig):
        btn = QPushButton(btnConfig["title"])
        btn.setIcon(qta.icon(btnConfig["icon"]))
        btn.setIconSize(QSize(20, 20))
        if "cmd" in btnConfig:
            btn.clicked.connect(
                lambda _, cmd=btnConfig["cmd"]: cmd(self.run_engine))
        tooltipMsg = addLineJumps(btnConfig["tooltip"])
        btn.setToolTip(tooltipMsg)
        if "enabled" in btnConfig:
            btn.setEnabled(btnConfig["enabled"])
        return btn

    def getControllerStack(self, cmdBtnDict):
        """
            Group the control buttons in a dynamic stack.
        """
        stack = QStackedWidget()
        for btnConfig in cmdBtnDict:
            btn = self.getSinglePushButton(btnConfig)
            stack.addWidget(btn)

        return stack

    def confirmationDialog(self):
        """
            Confirm the desired action.
        """
        msg = "This procedure will destroy the bluesky environment.\n" \
        "You should only use this if you a running plan is frozen and you " \
        "can't halt or abort it.\nAre you sure you want to proceed?"
        resCode = QMessageBox.question(self, "Destroy Bluesky Environment",
            msg)
        if resCode == QMessageBox.Yes:
            return True
        return False
    
    def handle_destroy(self):
        confirmation = self.confirmationDialog()
        if confirmation:
            self.run_engine.activate_env_destroy(True)
            self.run_engine.environment_destroy(timeout=5)

    def addDestroyButton(self, hlay):
        group = QGroupBox()
        group.setTitle("Destroy")
        groupLay = QHBoxLayout()
        groupLay.setContentsMargins(25, 2, 25, 2)
        group.setLayout(groupLay)

        btn = self.getSinglePushButton(CONFIG["destroy"])
        btn.clicked.connect(self.handle_destroy)
        groupLay.addWidget(btn)
        hlay.addWidget(group)
        
    def getQueueController(self):
        """
            Group the buttons stacks for controlling the queue.
        """
        group = QGroupBox()
        hlay = QHBoxLayout()
        group.setLayout(hlay)
        group.setTitle("Queue Controller")
        group.setMinimumWidth(300)
        hlay.setContentsMargins(25, 2, 25, 2)

        queue_stacks = ["start", "stop", "help"]
        if self.execution_monitor:
            queue_stacks = ["start_monitor", "stop", "help"]
        for cmdBtnKey in queue_stacks:
            self.addControlButton(cmdBtnKey, hlay)

        return group

    def setLogged(self):
        self.isLogged = True

    def handleLoginChanged(self, loginChanged):
        for stack in self.cmdStacks:
            stack.setEnabled(False)
            loginChanged.connect(stack.setEnabled)
        loginChanged.connect(self.setLogged)

    def _setupUi(self, loginChanged):
        hlay = QHBoxLayout(self)
        

        if not self.execution_monitor:
            self.addDestroyButton(hlay)
            self.addStatusLeds(hlay)
        else:
            self.cmdStacks.append(QStackedWidget())

        group = self.getQueueController()
        hlay.addWidget(group)

        self.updateEvent.connect(self.statusChanged)
        self.handleLoginChanged(loginChanged)
        self.setMaximumHeight(75)
