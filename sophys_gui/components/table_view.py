import qtawesome as qta
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QTableView, QHeaderView, \
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QPushButton

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


class SophysQueueTable(QWidget):

    def __init__(self, model):
        super().__init__()
        self.queueModel = QueueModel(model)
        self.serverModel = model
        self.loop = None
        self.cmd_btns = {}
        self.setMinimumWidth(350)
        self._setupUi()

    def updateLoopState(self, evt):
        if evt.is_connected:
            status = self.serverModel.run_engine.re_manager_status
            queueMode = status.get("plan_queue_mode", None)
            loopEnabled = queueMode.get("loop", None) if queueMode else None
            self.loop.slider.setValue(1 if loopEnabled else 0)

    def getHeader(self):
        hlay = QHBoxLayout()

        title = getHeader("Queue")
        hlay.addWidget(title)

        enable_loop = self.serverModel.run_engine.queue_mode_loop_enable
        self.serverModel.run_engine.events.status_changed.connect(
            self.updateLoopState)
        self.loop = SophysSwitchButton(
            "Loop", enable_loop)
        hlay.addWidget(self.loop)

        return hlay

    def handleCommand(self, cmd, model):
        cmd()
        updateIndex(model, self.cmd_btns)

    def create_btns(self, glay, btn_dict, model):
        idx = 0
        idy = 0
        for btn_dict in btn_dict:
            title = btn_dict["title"]
            permission = btn_dict["permission"]
            btn = QPushButton(title)
            btn.clicked.connect(
                lambda _, model=model, cmd=btn_dict["cmd"]: self.handleCommand(cmd, model))
            btn.setIcon(qta.icon(btn_dict["icon"]))
            btn.setEnabled(btn_dict["enabled"])
            self.cmd_btns[title] = {
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
                "permission": 3
            },
            {
                "title": "Up",
                "icon": "fa5s.arrow-up",
                "cmd": model.move_up,
                "enabled": False,
                "permission": 3
            },
            {
                "title": "Down",
                "icon": "fa5s.arrow-down",
                "cmd": model.move_down,
                "enabled": False,
                "permission": 2
            },
            {
                "title": "Bottom",
                "icon": "ri.align-bottom",
                "cmd": model.move_bottom,
                "enabled": False,
                "permission": 2
            },
            {
                "title": "Delete",
                "icon": "fa5s.trash-alt",
                "cmd": model.delete_item,
                "enabled": False,
                "permission": 1
            },
            {
                "title": "Duplicate",
                "icon": "fa5s.clone",
                "cmd": model.duplicate_item,
                "enabled": False,
                "permission": 1
            },
            {
                "title": "Copy",
                "icon": "fa5s.copy",
                "cmd": model.copy_queue_item,
                "enabled": False,
                "permission": 1
            },
            {
                "title": "Edit",
                "icon": "fa5s.pencil-alt",
                "cmd": model.edit_queue_item,
                "enabled": False,
                "permission": 1
            },
            {
                "title": "Clear All",
                "icon": "mdi.sort-variant-remove",
                "cmd": model.clear_all,
                "enabled": True,
                "permission": 0
            },
            {
                "title": "Add Plan",
                "icon": "fa5s.plus",
                "cmd": model.add_plan_item,
                "enabled": True,
                "permission": 0
            },
            {
                "title": "Add Instruction",
                "icon": "mdi6.block-helper",
                "cmd": model.add_instruction_item,
                "enabled": True,
                "permission": 0
            },
            {
                "title": "Add Stop Item",
                "icon": "mdi6.block-helper",
                "cmd": model.add_stop_queue,
                "enabled": True,
                "permission": 0
            }
        ]
        self.create_btns(glay, control_btns, model)

    def getTableControls(self, model):
        glay = QGridLayout()

        self.setCommandButtons(model, glay)

        return glay

    def _setupUi(self):
        vlay = QVBoxLayout(self)

        header = self.getHeader()
        vlay.addLayout(header)

        table = SophysTable(self.queueModel)
        self.queueModel.updateTable.connect(table.detectChange)
        vlay.addWidget(table)

        controls = self.getTableControls(table.model())
        vlay.addLayout(controls)

        table.pressed.connect(
            lambda _, model=table.model(),
            cmd_btns=self.cmd_btns: updateIndex(model, cmd_btns))

        self.setLayout(vlay)


class SophysHistoryTable(QWidget):

    def __init__(self, model):
        super().__init__()
        self.queueModel = HistoryModel(model)
        self.cmd_btns = {}
        self.setMinimumWidth(425)
        self._setupUi()

    def create_btns(self, glay, btn_dict):
        for idy, btn_dict in enumerate(btn_dict):
            title = btn_dict["title"]
            btn = QPushButton(title)
            btn.clicked.connect(btn_dict["cmd"])
            btn.setIcon(qta.icon(btn_dict["icon"]))
            btn.setEnabled(btn_dict["enabled"])
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
                "permission": 0
            },
            {
                "title": "Copy to Queue",
                "icon": "mdi6.content-copy",
                "cmd": model.copy_to_queue,
                "enabled": False,
                "permission": 1
            }
        ]
        self.create_btns(glay, control_btns)
        return glay

    def _setupUi(self):
        vlay = QVBoxLayout(self)

        header = getHeader("History")
        vlay.addWidget(header)

        table = SophysTable(self.queueModel)
        self.queueModel.updateTable.connect(table.detectChange)
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

    def detectChange(self, rowCount):
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
            if "Keyword" in item[0]:
                resize_pol = QHeaderView.Stretch
            hor_header.setSectionResizeMode(
                idcol, resize_pol)
