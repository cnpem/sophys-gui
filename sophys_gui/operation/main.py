from qtpy.QtWidgets import QMainWindow, QGridLayout, \
    QWidget
from sophys_gui.components import SophysQueueTable, \
    SophysHistoryTable, SophysRunningItem


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._setupUi()

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
