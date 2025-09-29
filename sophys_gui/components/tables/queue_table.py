import qtawesome as qta
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, \
    QWidget, QGridLayout, QPushButton

from sophys_gui.functions import getHeader, addLineJumps
from ..switch import SophysSwitchButton
from ..list_models import QueueModel
from .table_view import SophysTable
from .util import QUEUE_BTNS, QUEUE_TABLE_BTNS


class SophysQueueTable(QWidget):
    """
        Table widget customized for interacting and monitoring
        the Blueksy Queue.

        .. image:: ./_static/queue_table.png
            :width: 750
            :alt: Queue Table Widget
            :align: center

    """

    def __init__(self, model, loginChanged, reading_order, yml_file_path=None):
        super().__init__()
        self.queueModel = QueueModel(model, reading_order, yml_file_path)
        self.serverModel = model
        self.loop = None
        self.cmd_btns = {}
        self._setupUi(loginChanged)

    def getLoopStatus(self):
        """
            Return the if loop queue mode is enabled.
        """
        status = self.serverModel.run_engine.re_manager_status
        queueMode = status.get("plan_queue_mode", None)
        return queueMode.get("loop", None) if queueMode else None

    def updateLoopState(self, evt):
        """
            Update the loop widget based on its state.
        """
        if evt.is_connected:
            loopEnabled = self.getLoopStatus()
            if loopEnabled != self.loop.state:
                self.loop.slider.setValue(1 if loopEnabled else 0)
                self.loop.state = loopEnabled

    def getLoopSwitch(self):
        """
            Create Loop switch widget.
        """
        enable_loop = self.serverModel.run_engine.queue_mode_loop_enable
        self.serverModel.run_engine.events.status_changed.connect(
            self.updateLoopState)
        loop = SophysSwitchButton(
            "Loop", enable_loop, self.getLoopStatus())
        loopTooltip = addLineJumps("Enable looping the queue item. In this mode " \
            "the itens inside the queue list won't be delete and will be placed in the " \
            "last position of the queue after its completion. The queue will run until " \
            "a process fail, the loop is disabled or the queue is stopped or paused.")
        loop.setToolTip(loopTooltip)
        return loop

    def getHeader(self):
        """
            Create the Queue Table header.
        """
        hlay = QHBoxLayout()

        title = getHeader("Queue")
        hlay.addWidget(title)

        self.loop = self.getLoopSwitch()
        hlay.addWidget(self.loop)

        return hlay

    def handleCommand(self, cmd, title, hasConfirmation, row):
        """
            Handle button click.
        """
        confirmation = True
        if hasConfirmation:
            confirmation = self.table.confirmationDialog(title)
        if row!=None:
            self.queueModel.select(row)
        if confirmation:
            cmd(self.queueModel)
            self.table.updateIndex(self.cmd_btns)

    def createSingleBtn(self, btn_dict, idx=None):
        """
            Create a single button for interacting with the Bluesky Queue.
        """
        title = ""
        if "title" in btn_dict:
            title = btn_dict["title"]
        btn = QPushButton(title)
        btn.setMaximumHeight(50)
        hasConfirmation = "confirm" in btn_dict
        btn.clicked.connect(
            lambda _, cmd=btn_dict["cmd"],
            title=title, hasConf=hasConfirmation, idx=idx: self.handleCommand(
                cmd, title, hasConf, idx))
        btn.setIcon(qta.icon(btn_dict["icon"]))
        btn.setEnabled(btn_dict["enabled"])
        tooltipMsg = addLineJumps(btn_dict["tooltip"])
        btn.setToolTip(tooltipMsg)
        return btn

    def getTableControls(self):
        """
            Create all buttons for interacting with the Bluesky Queue.
        """
        glay = QGridLayout()
        idx = 0
        idy = 0
        for btn_dict in QUEUE_BTNS:
            permission = btn_dict["permission"]
            btn = self.createSingleBtn(btn_dict)
            self.cmd_btns[btn_dict["title"]] = {
                "btn": btn,
                "permission": permission
            }
            glay.addWidget(btn, idx, idy, 1, 1)
            idy += 1
            if idy%4==0:
                idx += 1
                idy = 0

        return glay

    def setTableOperationButtons(self, table, rowCount=None):
        """
            Create buttons inside a table row for interacting with
            that specific plan.
        """
        rows = self.queueModel.rowCount()
        colCount = self.queueModel.columnCount()-2
        self.cmd_btns["table"] = {}
        for idx in range(0, rows):
            for idy, btn_dict in enumerate(QUEUE_TABLE_BTNS):
                btn = self.createSingleBtn(btn_dict, idx)
                table.setIndexWidget(self.queueModel.index(idx, colCount+idy), btn)
                self.cmd_btns["table"][f"{idx}__{idy}"] = {
                    "btn": btn,
                    "permission": 0
                }

        if rowCount:
            table.detectChange(rowCount, self.cmd_btns)

    def handleLoginChanged(self, loginChanged, table):
        """
            Handle login or logout permissions.
        """
        loginChanged.connect(
            lambda loginStatus: table.setLogin(loginStatus, self.cmd_btns))
        self.loop.setEnabled(False)
        loginChanged.connect(self.loop.setEnabled)

    def _setupUi(self, loginChanged):
        vlay = QVBoxLayout(self)

        header = self.getHeader()
        vlay.addLayout(header)

        table = SophysTable(self.queueModel)
        self.table = table
        vlay.addWidget(table)

        self.setTableOperationButtons(table)

        controls = self.getTableControls()
        vlay.addLayout(controls)

        self.queueModel.updateTable.connect(
            lambda rowCount, table=table: self.setTableOperationButtons(table, rowCount))
        self.queueModel.updateTable.connect(
            lambda _, cmd_btns=self.cmd_btns: table.updateIndex(cmd_btns))
        table.pressed.connect(
            lambda _, cmd_btns=self.cmd_btns: table.updateIndex(cmd_btns))

        self.handleLoginChanged(loginChanged, table)
