from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QTableView, QHeaderView, \
    QVBoxLayout, QHBoxLayout, QWidget, QLabel
from .switch import SophysSwitchButton


class SophysQueueTable(QWidget):

    def __init__(self, model, backend_model):
        super().__init__()
        self.queueModel = model
        self.serverModel = backend_model
        self.loop = None
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

    def _setupUi(self):
        vlay = QVBoxLayout(self)

        header = self.getHeader()
        vlay.addLayout(header)

        table = SophysTable(self.queueModel)
        vlay.addWidget(table)

        self.setLayout(vlay)

class SophysTable(QTableView):

    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        columns = model.getColumns()
        self.setResizable(columns)

    def setResizable(self, columns):
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        hor_header = self.horizontalHeader()
        for idcol, item in enumerate(columns):
            resize_pol = QHeaderView.ResizeToContents
            if "Keyword" in item[0]:
                resize_pol = QHeaderView.Stretch
            hor_header.setSectionResizeMode(
                idcol, resize_pol)
