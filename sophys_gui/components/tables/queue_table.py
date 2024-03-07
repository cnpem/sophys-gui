import qtawesome as qta
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, \
    QWidget, QGridLayout, QPushButton

from sophys_gui.functions import getHeader
from ..switch import SophysSwitchButton
from ..list_models import QueueModel
from .table_view import SophysTable


class SophysQueueTable(QWidget):

    def __init__(self, model, loginChanged):
        super().__init__()
        self.queueModel = QueueModel(model)
        self.serverModel = model
        self.loop = None
        self.cmd_btns = {}
        self._setupUi(loginChanged)

    def getLoopStatus(self):
        status = self.serverModel.run_engine.re_manager_status
        queueMode = status.get("plan_queue_mode", None)
        return queueMode.get("loop", None) if queueMode else None

    def updateLoopState(self, evt):
        if evt.is_connected:
            loopEnabled = self.getLoopStatus()
            if loopEnabled != self.loop.state:
                self.loop.slider.setValue(1 if loopEnabled else 0)
                self.loop.state = loopEnabled

    def getHeader(self):
        hlay = QHBoxLayout()

        title = getHeader("Queue")
        hlay.addWidget(title)

        enable_loop = self.serverModel.run_engine.queue_mode_loop_enable
        self.serverModel.run_engine.events.status_changed.connect(
            self.updateLoopState)
        self.loop = SophysSwitchButton(
            "Loop", enable_loop, self.getLoopStatus())
        self.loop.setToolTip("Enable looping the queue item. In this mode "
            "the itens inside the queue list won't be delete and will be placed in the "
            "last position of the queue after its completion. The queue will run until "
            "a process fail, the loop is disabled or the queue is stopped or paused.")
        hlay.addWidget(self.loop)

        return hlay

    def handleCommand(self, cmd, title, hasConfirmation, row):
        confirmation = True
        if hasConfirmation:
            confirmation = self.table.confirmationDialog(title)
        if row!=None:
            self.queueModel.select(row)
        if confirmation:
            cmd()
            self.table.updateIndex(self.cmd_btns)

    def createSingleBtn(self, btn_dict, model, idx=None):
        title = ""
        if "title" in btn_dict:
            title = btn_dict["title"]
        btn = QPushButton(title)
        btn.setMaximumHeight(50)
        hasConfirmation = "confirm" in btn_dict
        btn.clicked.connect(
            lambda _, model=model, cmd=btn_dict["cmd"],
            title=title, hasConf=hasConfirmation, idx=idx: self.handleCommand(
                cmd, title, hasConf, idx))
        btn.setIcon(qta.icon(btn_dict["icon"]))
        btn.setEnabled(btn_dict["enabled"])
        btn.setToolTip(btn_dict["tooltip"])
        return btn

    def createBtns(self, glay, btn_dict, model):
        idx = 0
        idy = 0
        for btn_dict in btn_dict:
            permission = btn_dict["permission"]
            btn = self.createSingleBtn(btn_dict, model)
            self.cmd_btns[btn_dict["title"]] = {
                "btn": btn,
                "permission": permission
            }
            glay.addWidget(btn, idx, idy, 1, 1)
            idy += 1
            if idy%4==0:
                idx += 1
                idy = 0

    def setCommandButtons(self, model, glay):
        control_btns = [
            {
                "title": "Top",
                "icon": "ri.align-top",
                "cmd": model.move_top,
                "enabled": False,
                "permission": 3,
                "tooltip": "Move the selected item to the first position of the queue."
            },
            {
                "title": "Up",
                "icon": "fa5s.arrow-up",
                "cmd": model.move_up,
                "enabled": False,
                "permission": 3,
                "tooltip": "Move the selected item to one position ahead in the queue."
            },
            {
                "title": "Down",
                "icon": "fa5s.arrow-down",
                "cmd": model.move_down,
                "enabled": False,
                "permission": 2,
                "tooltip": "Move the selected item to one position back in the queue."
            },
            {
                "title": "Bottom",
                "icon": "ri.align-bottom",
                "cmd": model.move_bottom,
                "enabled": False,
                "permission": 2,
                "tooltip": "Move the selected item to the last position of the queue."
            },
            {
                "title": "Delete",
                "icon": "fa5s.trash-alt",
                "cmd": model.delete_item,
                "enabled": False,
                "confirm": True,
                "permission": 1,
                "tooltip": "Delete the selected item from the queue."
            },
            {
                "title": "Duplicate",
                "icon": "fa5s.clone",
                "cmd": model.duplicate_item,
                "enabled": False,
                "permission": 1,
                "tooltip": "Duplicate the selected item data into a new queue "\
                    "item that will be placed after the selected item."
            },
            {
                "title": "Copy",
                "icon": "fa5s.copy",
                "cmd": model.copy_queue_item,
                "enabled": False,
                "permission": 1,
                "tooltip": "Copy the selected item data into a form for creating a " \
                    "new queue item that will be placed after the selected item."
            },
            {
                "title": "Edit",
                "icon": "fa5s.pencil-alt",
                "cmd": model.edit_queue_item,
                "enabled": False,
                "permission": 1,
                "tooltip": "Copy the selected item data into a form that will " \
                    "update selected item."
            },
            {
                "title": "Clear All",
                "icon": "mdi.sort-variant-remove",
                "cmd": model.clear_all,
                "enabled": True,
                "confirm": True,
                "permission": 0,
                "tooltip": "Delete all the queue items."
            },
            {
                "title": "Add Plan",
                "icon": "fa5s.plus",
                "cmd": model.add_plan_item,
                "enabled": True,
                "permission": 0,
                "tooltip": "Open a form that will create a new queue item " \
                    "and placed it in the last position of the queue."
            },
            {
                "title": "Add Instruction",
                "icon": "mdi6.block-helper",
                "cmd": model.add_instruction_item,
                "enabled": True,
                "permission": 0,
                "tooltip": "Add a customized instruction " \
                    "and placed it in the last position of the queue."
            },
            {
                "title": "Add Stop Item",
                "icon": "mdi6.block-helper",
                "cmd": model.add_stop_queue,
                "enabled": True,
                "permission": 0,
                "tooltip": "Add an instruction for stopping the queue " \
                    "and placed it in the last position of the queue."
            }
        ]
        self.createBtns(glay, control_btns, model)

    def getTableControls(self, model):
        glay = QGridLayout()

        self.setCommandButtons(model, glay)

        return glay

    def setTableOperationButtons(self, table):
        rows = self.queueModel.rowCount()
        colCount = self.queueModel.columnCount()-2
        self.cmd_btns["table"] = {}
        for idx in range(0, rows):
            control_btns = [
                {
                    "icon": "fa5s.pencil-alt",
                    "cmd": self.queueModel.edit_queue_item,
                    "enabled": True,
                    "tooltip": "",
                    "permission": 0
                },
                {
                    "icon": "fa5s.trash-alt",
                    "cmd": self.queueModel.delete_item,
                    "enabled": True,
                    "confirm": True,
                    "tooltip": "",
                    "permission": 0
                }
            ]
            for idy, btn_dict in enumerate(control_btns):
                btn = self.createSingleBtn(btn_dict, self.queueModel, idx)
                table.setIndexWidget(self.queueModel.index(idx, colCount+idy), btn)
                self.cmd_btns["table"][f"{idx}__{idy}"] = {
                    "btn": btn,
                    "permission": 0
                }

    def handleLoginChanged(self, loginChanged, table):
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
        self.queueModel.updateTable.connect(
            lambda _, table=table: self.setTableOperationButtons(table))

        controls = self.getTableControls(table.model())
        vlay.addLayout(controls)

        self.queueModel.updateTable.connect(
            lambda rowCount: table.detectChange(rowCount, self.cmd_btns))
        table.pressed.connect(
            lambda _, cmd_btns=self.cmd_btns: table.updateIndex(cmd_btns))

        self.handleLoginChanged(loginChanged, table)
