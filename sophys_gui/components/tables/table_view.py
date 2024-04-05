from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QTableView, QHeaderView, QMessageBox


class SophysTable(QTableView):
    """
        General table widget for interacting with the Queue Server.
    """

    def __init__(self, model):
        super().__init__()
        self.currRows = 0
        self.setModel(model)
        self.setResizable()
        self.timer=QTimer()
        self.loginStatus = False
        self.timer.timeout.connect(self.resetBorder)
        self.pressed.connect(self.selectItem)

    def resetBorder(self):
        self.setStyleSheet("QTableView{ border: 1px solid #ddd;}")
        self.timer.stop()

    def getLimitsPermissions(self, sel_row, condition):
        """
            Get if the button has the necessary upper or lower permissions.
        """
        status = True
        for item in sel_row:
            if condition(item):
                status = False
        return status

    def handleBtnEnabled(self, permission, model):
        """
            Get if the button has the necessary permissions.
        """
        permissionList = [
            "all",
            "hasSelectedItem",
            "lowLimit",
            "upperLimit"
        ]
        permission = permissionList[permission]
        notLoggedIn = not self.loginStatus
        if notLoggedIn:
            return False
        if permission == "all":
            return True
        noRows = model.rowCount()==0
        if noRows:
            return False
        selected_rows = model.getSelectedRows()
        hasSelectedRows = len(selected_rows) > 0
        if hasSelectedRows:
            if permission == "lowLimit":
                rows = model.rowCount()
                return self.getLimitsPermissions(
                    selected_rows, lambda idx, rows=rows: (idx+1) >= rows)
            if permission == "upperLimit":
                return self.getLimitsPermissions(
                    selected_rows, lambda idx: idx <= 0)
            return True
        return False

    def updateIndex(self, cmd_btns):
        """
            Update the GUI permissions status.
        """
        for key, value in cmd_btns.items():
            if key == "table":
                self.updateIndex(value)
            else:
                status = self.handleBtnEnabled(value["permission"], self.model())
                cmd_btns[key]["btn"].setEnabled(status)

    def setLogin(self, loginStatus, cmd_btns):
        """
            Handle the permission for the login and logout.
        """
        self.loginStatus = loginStatus
        self.updateIndex(cmd_btns)

    def confirmationDialog(self, title):
        """
            Confirm the desired action.
        """
        resCode = QMessageBox.question(self, title + " Action Confirmation",
            "Are you sure you want to proceed?")
        if resCode == QMessageBox.Yes:
            return True
        return False

    def detectChange(self, rowCount, cmd_btns):
        """
            Handle the permission when the table changes and shows
            a border color animation based on the addition or removal
            of a row.
        """
        self.updateIndex(cmd_btns)
        additionChange = rowCount > self.currRows
        deletionChange = rowCount < self.currRows
        if deletionChange:
            self.setStyleSheet("QTableView{ border: 1px solid #ff0000;}")
        elif additionChange:
            self.setStyleSheet("QTableView{ border: 1px solid #00ff00;}")
        self.currRows = rowCount
        self.timer.start(1000)

    def selectItem(self):
        """
            Select row.
        """
        table_model = self.model()
        row = self.currentIndex().row()
        table_model.select(row)

    def setHorizontalResizePolicy(self):
        """
            Handle the table horizontal resizing.
        """
        columns = self.model().getColumns()
        hor_header = self.horizontalHeader()
        for idcol, item in enumerate(columns):
            resize_pol = QHeaderView.ResizeToContents
            isArgs = "Arguments" in item[0]
            if isArgs:
                resize_pol = QHeaderView.Stretch
            hor_header.setSectionResizeMode(
                idcol, resize_pol)

    def setResizable(self):
        """
            Handle the table resizing.
        """
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.setHorizontalResizePolicy()
