import qtawesome as qta
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QTableView, QHeaderView, \
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QPushButton, \
    QMessageBox

from sophys_gui.functions import getHeader
from .switch import SophysSwitchButton
from .list_models import QueueModel, HistoryModel


def getLimitsPermissions(sel_row, condition):
    status = True
    for item in sel_row:
        if condition(item):
            status = False
    return status

def handleBtnEnabled(permission, model):
    if permission == 0:
        return True
    if model.rowCount()==0:
        return False
    selected_rows = model.getSelectedRows()
    if len(selected_rows) > 0:
        if permission == 2:
            rows = model.rowCount()
            status = getLimitsPermissions(
                selected_rows, lambda idx, rows=rows: (idx+1) >= rows)
        elif permission == 3:
            status = getLimitsPermissions(
                selected_rows, lambda idx: idx <= 0)
        else:
            status = True
    else:
        status = False

    return status

def updateIndex(model, cmd_btns):
    for key, value in cmd_btns.items():
        status = handleBtnEnabled(value["permission"], model)
        cmd_btns[key]["btn"].setEnabled(status)

def confirmationDialog(parent, title):
    resCode = QMessageBox.question(parent, title + " Action Confirmation",
        "Are you sure you want to proceed?")
    if resCode == QMessageBox.Yes:
        return True
    return False


class SophysQueueTable(QWidget):

    def __init__(self, model):
        super().__init__()
        self.queueModel = QueueModel(model)
        self.serverModel = model
        self.loop = None
        self.cmd_btns = {}
        self._setupUi()

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

    def handleCommand(self, cmd, model, title, hasConfirmation, row):
        confirmation = True
        if hasConfirmation:
            confirmation = confirmationDialog(self, title)
        if row!=None:
            self.queueModel.select(row)
        if confirmation:
            cmd()
            updateIndex(model, self.cmd_btns)

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
                cmd, model, title, hasConf, idx))
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
        for idx in range(0, rows):
            control_btns = [
                {
                    "icon": "fa5s.pencil-alt",
                    "cmd": self.queueModel.edit_queue_item,
                    "enabled": True,
                    "tooltip": ""
                },
                {
                    "icon": "fa5s.trash-alt",
                    "cmd": self.queueModel.delete_item,
                    "enabled": True,
                    "confirm": True,
                    "tooltip": ""
                }
            ]
            for idy, btn_dict in enumerate(control_btns):
                btn = self.createSingleBtn(btn_dict, self.queueModel, idx)
                table.setIndexWidget(self.queueModel.index(idx, colCount+idy), btn)

    def _setupUi(self):
        vlay = QVBoxLayout(self)

        header = self.getHeader()
        vlay.addLayout(header)

        table = SophysTable(self.queueModel)
        self.queueModel.updateTable.connect(
            lambda rowCount: table.detectChange(rowCount, self.cmd_btns))
        vlay.addWidget(table)

        controls = self.getTableControls(table.model())
        vlay.addLayout(controls)

        table.pressed.connect(
            lambda _, model=table.model(),
            cmd_btns=self.cmd_btns: updateIndex(model, cmd_btns))
        self.setTableOperationButtons(table)
        self.queueModel.updateTable.connect(
            lambda _, table=table: self.setTableOperationButtons(table))

        self.setLayout(vlay)


class SophysHistoryTable(QWidget):

    def __init__(self, model):
        super().__init__()
        self.queueModel = HistoryModel(model)
        self.cmd_btns = {}
        self._setupUi()

    def handleCommand(self, cmd, title, hasConfirmation):
        confirmation = True
        if hasConfirmation:
            confirmation = confirmationDialog(self, title)
        if confirmation:
            cmd()
            updateIndex(self.queueModel, self.cmd_btns)

    def createBtns(self, glay, btn_dict):
        for idy, btn_dict in enumerate(btn_dict):
            title = btn_dict["title"]
            btn = QPushButton(title)
            hasConfirmation = "confirm" in btn_dict
            btn.clicked.connect(lambda _, hasConf=hasConfirmation,
                cmd=btn_dict["cmd"], title=title: self.handleCommand(cmd, title, hasConf))
            btn.setIcon(qta.icon(btn_dict["icon"]))
            btn.setEnabled(btn_dict["enabled"])
            btn.setToolTip(btn_dict["tooltip"])
            self.cmd_btns[title] = {
                "btn": btn,
                "permission": btn_dict["permission"]
            }
            glay.addWidget(btn, 1, idy, 1, 1)

    def getTableControls(self, model):
        glay = QGridLayout()
        control_btns = [
            {
                "title": "Clear All",
                "icon": "mdi.sort-variant-remove",
                "cmd": model.clear_all,
                "enabled": True,
                "confirm": True,
                "permission": 0,
                "tooltip": "Delete all the history items."
            },
            {
                "title": "Copy to Queue",
                "icon": "mdi6.content-copy",
                "cmd": model.copy_to_queue,
                "enabled": False,
                "permission": 1,
                "tooltip": "Duplicate the selected item to the end of the queue list."
            }
        ]
        self.createBtns(glay, control_btns)
        return glay

    def _setupUi(self):
        vlay = QVBoxLayout(self)

        header = getHeader("History")
        vlay.addWidget(header)

        table = SophysTable(self.queueModel)
        self.queueModel.updateTable.connect(
            lambda rowCount: table.detectChange(rowCount, self.cmd_btns))
        vlay.addWidget(table)

        controls = self.getTableControls(table.model())
        vlay.addLayout(controls)

        table.pressed.connect(
            lambda _, model=table.model(),
            cmd_btns=self.cmd_btns: updateIndex(model, cmd_btns))

        self.setLayout(vlay)


class SophysTable(QTableView):

    def __init__(self, model):
        super().__init__()
        self.currRows = 0
        self.setModel(model)
        self.setResizable()
        self.timer=QTimer()
        self.timer.timeout.connect(self.resetBorder)
        self.pressed.connect(self.selectItem)

    def resetBorder(self):
        self.setStyleSheet("QTableView{ border: 1px solid #ddd;}")
        self.timer.stop()

    def detectChange(self, rowCount, cmd_btns):
        updateIndex(self.model(), cmd_btns)
        if rowCount < self.currRows:
            self.setStyleSheet("QTableView{ border: 1px solid #ff0000;}")
        elif rowCount > self.currRows:
            self.setStyleSheet("QTableView{ border: 1px solid #00ff00;}")
        self.currRows = rowCount
        self.timer.start(1000)

    def selectItem(self):
        table_model = self.model()
        row = self.currentIndex().row()
        table_model.select(row)

    def setResizable(self):
        columns = self.model().getColumns()
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        hor_header = self.horizontalHeader()
        for idcol, item in enumerate(columns):
            resize_pol = QHeaderView.ResizeToContents
            if "Arguments" in item[0]:
                resize_pol = QHeaderView.Stretch
            hor_header.setSectionResizeMode(
                idcol, resize_pol)
