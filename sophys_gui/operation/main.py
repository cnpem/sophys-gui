from qtpy.QtWidgets import QMainWindow, QGridLayout, \
    QWidget
from sophys_gui.components import SophysQueueTable, \
    SophysHistoryTable, SophysRunningItem, QueueController


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._setupUi()

    def _setupUi(self):
        wid = QWidget()
        glay = QGridLayout()
        wid.setLayout(glay)

        controller = QueueController(self.model)
        glay.addWidget(controller, 0, 0, 1, 3)

        queue = SophysQueueTable(self.model)
        glay.addWidget(queue, 1, 0, 1, 1)

        running = SophysRunningItem(self.model)
        glay.addWidget(running, 1, 1, 1, 1)

        history = SophysHistoryTable(self.model)
        glay.addWidget(history, 1, 2, 1, 1)

        self.setCentralWidget(wid)
