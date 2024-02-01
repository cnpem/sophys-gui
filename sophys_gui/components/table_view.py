import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTableView, QHeaderView, \
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout, \
    QPushButton
from .switch import SophysSwitchButton


class SophysQueueTable(QWidget):

    def __init__(self, model, backend_model):
        super().__init__()
        self.queueModel = model
        self.serverModel = backend_model
        self.loop = None
        self.cmd_btns = {}
        self._setupUi()

    def updateLoopState(self, evt):
        status = self.serverModel.run_engine.re_manager_status
        queueMode = status.get("plan_queue_mode", None)
        loopEnabled = queueMode.get("loop", None) if queueMode else None
        self.loop.slider.setValue(1 if loopEnabled else 0)

    def getHeader(self):
        hlay = QHBoxLayout()

        title = QLabel("Queue")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            """
                font-weight: 800;
                font-size: 18px;
            """
        )
        hlay.addWidget(title)

        enable_loop = self.serverModel.run_engine.queue_mode_loop_enable
        self.serverModel.run_engine.events.status_changed.connect(
            self.updateLoopState)
        self.loop = SophysSwitchButton(
            "Loop", enable_loop)
        hlay.addWidget(self.loop)

        return hlay

    def getLimitsPermissions(self, sel_row, condition):
        status = True
        for item in sel_row:
            if condition(item):
                status = False
        return status

    def handleBtnEnabled(self, permission, key, model):
        if permission == 0:
            return
        selected_rows = model.getSelectedRows()
        if len(selected_rows) > 0:
            if permission == 2:
                rows = model.rowCount()
                status = self.getLimitsPermissions(
                    selected_rows, lambda idx, rows=rows: (idx+1) >= rows)
            elif permission == 3:
                status = self.getLimitsPermissions(
                    selected_rows, lambda idx: idx <= 0)
            else:
                status = True
        else:
            status = False
        self.cmd_btns[key]["btn"].setEnabled(status)

    def updateIndex(self, model):
        for key, value in self.cmd_btns.items():
            self.handleBtnEnabled(value["permission"], key, model)

    def handleCommand(self, cmd, model):
        cmd()
        self.updateIndex(model)

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
                "title": "Clear",
                "icon": "mdi.sort-variant-remove",
                "cmd": model.move_bottom,
                "enabled": True,
                "permission": 0
            },
            {
                "title": "Delete",
                "icon": "fa5s.trash-alt",
                "cmd": model.move_top,
                "enabled": False,
                "permission": 1
            },
            {
                "title": "Copy",
                "icon": "mdi6.content-copy",
                "cmd": model.move_up,
                "enabled": False,
                "permission": 1
            },
            {
                "title": "Edit",
                "icon": "fa5s.pencil-alt",
                "cmd": model.move_up,
                "enabled": True,
                "permission": 0
            },
            {
                "title": "Add",
                "icon": "fa5s.plus",
                "cmd": model.move_up,
                "enabled": True,
                "permission": 0
            },
            {
                "title": "Stop",
                "icon": "mdi6.block-helper",
                "cmd": model.move_up,
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
        table.pressed.connect(
            lambda _, model=table.model(): self.updateIndex(model))
        vlay.addWidget(table)

        controls = self.getTableControls(table.model())
        vlay.addLayout(controls)

        self.setLayout(vlay)


class SophysTable(QTableView):

    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setResizable()
        self.pressed.connect(self.selectItem)

    def selectItem(self):
        table_model = self.model()
        row = self.currentIndex().row()
        table_model.select(row)

    def setResizable(self):
        columns = self.model().getColumns()
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        hor_header = self.horizontalHeader()
        for idcol, item in enumerate(columns):
            resize_pol = QHeaderView.ResizeToContents
            if "Keyword" in item[0]:
                resize_pol = QHeaderView.Stretch
            hor_header.setSectionResizeMode(
                idcol, resize_pol)
