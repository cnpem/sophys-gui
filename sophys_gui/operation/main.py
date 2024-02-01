from qtpy.QtWidgets import QMainWindow, QGridLayout, \
    QWidget
from sophys_gui.components import QueueModel, \
    SophysQueueTable


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._setupUi()

    def _setupUi(self):
        wid = QWidget()
        glay = QGridLayout()
        wid.setLayout(glay)

        model = QueueModel(self.model)
        queue = SophysQueueTable(model, self.model)
        glay.addWidget(queue, 0, 0, 1, 1)

        self.setCentralWidget(wid)
