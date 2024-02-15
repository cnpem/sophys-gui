from qtpy.QtWidgets import QMainWindow, QGridLayout, \
    QWidget
from sophys_gui.components import SophysQueueTable, \
    SophysHistoryTable, SophysRunningItem, QueueController
from kafka_bluesky_live.live_view import LiveView
from suitscase import LoginCNPEM


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._setupUi()

    def loginUser(self, isLogged):
        re = self.model.run_engine
        if isLogged:
            re._user_name = self.login._email.text()
            re._user_group = self.login._allowed_group
            self.login._email.setText("")
            self.login._password.setText("")
        else:
            re._user_name = 'Unknown'
            re._user_group = 'Unknown'

    def _setupUi(self):
        wid = QWidget()
        glay = QGridLayout()
        wid.setLayout(glay)

        controller = QueueController(self.model)
        glay.addWidget(controller, 0, 0, 1, 2)

        self.login = LoginCNPEM(group="SWC")
        self.login.login_signal.connect(self.loginUser)
        self.login._email.setMinimumWidth(150)
        self.login._password.setMinimumWidth(150)
        glay.addWidget(self.login, 0, 2, 1, 1)

        queue = SophysQueueTable(self.model)
        glay.addWidget(queue, 1, 0, 1, 1)

        running = SophysRunningItem(self.model)
        glay.addWidget(running, 1, 1, 1, 1)

        history = SophysHistoryTable(self.model)
        glay.addWidget(history, 1, 2, 1, 1)

        live_view = LiveView('TEST_BL_bluesky', '127.0.0.1:kakfa_port')
        glay.addWidget(live_view, 2, 0, 1, 3)

        self.setCentralWidget(wid)
