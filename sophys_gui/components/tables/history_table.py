
from qtpy.QtWidgets import QVBoxLayout, QWidget, \
    QGridLayout, QPushButton

from sophys_gui.functions import getHeader
from ..list_models import HistoryModel
from .table_view import SophysTable


class SophysHistoryTable(QWidget):

    def __init__(self, model, loginChanged):
        super().__init__()
        self.queueModel = HistoryModel(model)
        self.cmd_btns = {}
        self._setupUi(loginChanged)

    def handleCommand(self, cmd, title, hasConfirmation):
        confirmation = True
        if hasConfirmation:
            confirmation = self.table.confirmationDialog(title)
        if confirmation:
            cmd()
            self.table.updateIndex(self.cmd_btns)

    def createBtns(self, glay, btn_dict):
        for idy, btn_dict in enumerate(btn_dict):
            title = btn_dict["title"]
            btn = QPushButton(title)
            hasConfirmation = "confirm" in btn_dict
            btn.clicked.connect(lambda _, hasConf=hasConfirmation,
                cmd=btn_dict["cmd"], title=title: self.handleCommand(cmd, title, hasConf))

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

    def handleLoginChanged(self, loginChanged, table):
        loginChanged.connect(
            lambda loginStatus: table.setLogin(loginStatus, self.cmd_btns))

    def _setupUi(self, loginChanged):
        vlay = QVBoxLayout(self)

        header = getHeader("History")
        vlay.addWidget(header)

        table = SophysTable(self.queueModel)
        vlay.addWidget(table)

        controls = self.getTableControls(table.model())
        vlay.addLayout(controls)

        self.queueModel.updateTable.connect(
            lambda rowCount: table.detectChange(rowCount, self.cmd_btns))
        table.pressed.connect(
            lambda _, cmd_btns=self.cmd_btns: table.updateIndex(cmd_btns))
        self.table = table

        self.handleLoginChanged(loginChanged, table)
