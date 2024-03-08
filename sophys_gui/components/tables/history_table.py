import qtawesome as qta
from qtpy.QtWidgets import QVBoxLayout, QWidget, \
    QGridLayout, QPushButton

from sophys_gui.functions import getHeader
from ..list_models import HistoryModel
from .table_view import SophysTable
from .util import HISTORY_BTNS


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
            cmd(self.queueModel)
            self.table.updateIndex(self.cmd_btns)

    def createBtns(self, title, btn_dict):
        btn = QPushButton(title)
        hasConfirmation = "confirm" in btn_dict
        btn.clicked.connect(lambda _, hasConf=hasConfirmation,
            cmd=btn_dict["cmd"], title=title, : self.handleCommand(cmd, title, hasConf))
        btn.setIcon(qta.icon(btn_dict["icon"]))
        btn.setEnabled(btn_dict["enabled"])
        btn.setToolTip(btn_dict["tooltip"])
        return btn

    def getTableControls(self):
        glay = QGridLayout()
        for idy, btn_dict in enumerate(HISTORY_BTNS):
            key = btn_dict["title"]
            btn = self.createBtns(key, btn_dict)
            self.cmd_btns[key] = {
                "btn": btn,
                "permission": btn_dict["permission"]
            }
            glay.addWidget(btn, 1, idy, 1, 1)

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

        controls = self.getTableControls()
        vlay.addLayout(controls)

        self.queueModel.updateTable.connect(
            lambda rowCount: table.detectChange(rowCount, self.cmd_btns))
        table.pressed.connect(
            lambda _, cmd_btns=self.cmd_btns: table.updateIndex(cmd_btns))
        self.table = table

        self.handleLoginChanged(loginChanged, table)
