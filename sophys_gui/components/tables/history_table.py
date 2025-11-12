import qtawesome as qta
from qtpy.QtWidgets import QVBoxLayout, QWidget, \
    QGridLayout, QPushButton

from sophys_gui.functions import getHeader, addLineJumps
from ..list_models import HistoryModel
from .table_view import SophysTable
from .util import HISTORY_BTNS


class SophysHistoryTable(QWidget):
    """
        Table widget customized for interacting and monitoring
        the Blueksy History.

        .. image:: ./_static/history_table.png
            :width: 750
            :alt: History Table Widget
            :align: center

    """

    def __init__(self, model, loginChanged, yml_file_path):
        super().__init__()
        self.queueModel = HistoryModel(model, yml_file_path)
        self.cmd_btns = {}
        self.index = 0
        self._setupUi(loginChanged)

    def handleCommand(self, cmd, title, hasConfirmation):
        """
            Handle button click.
        """
        confirmation = True
        if hasConfirmation:
            confirmation = self.table.confirmationDialog(title)
        if confirmation:
            cmd(self.queueModel)
            self.table.updateIndex(self.cmd_btns)

    def createBtns(self, title, btn_dict):
        """
            Create one button for interacting with the Bluesky History.
        """
        btn = QPushButton(title)
        hasConfirmation = "confirm" in btn_dict
        btn.clicked.connect(lambda _, hasConf=hasConfirmation,
            cmd=btn_dict["cmd"], title=title, : self.handleCommand(cmd, title, hasConf))
        btn.setIcon(qta.icon(btn_dict["icon"]))
        btn.setEnabled(btn_dict["enabled"])
        tooltipMsg = addLineJumps(btn_dict["tooltip"])
        btn.setToolTip(tooltipMsg)
        return btn

    def getTableControls(self):
        """
            Create all buttons for interacting with the Bluesky History.
        """
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
        """
            Handle login or logout permissions.
        """
        loginChanged.connect(
            lambda loginStatus: table.setLogin(loginStatus, self.cmd_btns))

    def detectScroll(self, index):
        self.index = index
        self.queueModel.visible_rows = (
            self.queueModel.rowCount() - index - 25,
            self.queueModel.rowCount() - index
        )

    def rowCountUpdate(self, rowCount):
        self.detectScroll(self.index)
        self.table.detectChange(rowCount, self.cmd_btns)

    def _setupUi(self, loginChanged):
        vlay = QVBoxLayout(self)

        header = getHeader("History")
        vlay.addWidget(header)

        table = SophysTable(self.queueModel)
        vlay.addWidget(table)

        controls = self.getTableControls()
        vlay.addLayout(controls)

        self.queueModel.updateTable.connect(self.rowCountUpdate)
        table.pressed.connect(
            lambda _, cmd_btns=self.cmd_btns: table.updateIndex(cmd_btns))
        table.verticalScrollBar().valueChanged.connect(self.detectScroll)
        self.table = table

        self.handleLoginChanged(loginChanged, table)
