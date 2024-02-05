import json
from qtpy.QtWidgets import QMainWindow, QGridLayout, \
    QWidget
from sophys_gui.components import SophysQueueTable, \
    SophysHistoryTable, SophysRunningItem
from sophys_gui.functions import getFilePath


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._setupUi()

    def setVariables(self, stylesheet):
        file = getFilePath("_assets/css-variables.json")
        variables = json.load(open(file))
        for key, value in variables.items():
            stylesheet = stylesheet.replace(key, value)
        return stylesheet

    def setStyle(self):
        """
            Generate a generic style for the applications.
        """
        style_file = getFilePath("_assets/css-style.css")
        with open(style_file, 'r') as f:
            style = f.read()
        style = self.setVariables(style)
        self.setStyleSheet(style)

    def _setupUi(self):
        wid = QWidget()
        glay = QGridLayout()
        wid.setLayout(glay)

        queue = SophysQueueTable(self.model)
        glay.addWidget(queue, 0, 0, 1, 1)

        running = SophysRunningItem(self.model)
        glay.addWidget(running, 0, 1, 1, 1)

        history = SophysHistoryTable(self.model)
        glay.addWidget(history, 0, 2, 1, 1)

        self.setCentralWidget(wid)

        self.setStyle()
