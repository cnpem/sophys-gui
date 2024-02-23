from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow, QWidget, QSplitter, \
    QGridLayout
from sophys_gui.components import SophysQueueTable, \
    SophysHistoryTable, SophysRunningItem, QueueController
from kafka_bluesky_live.live_view import LiveView
from suitscase import LoginCNPEM


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.client_data = None
        self._setupUi()

    def closeEvent(self, event):
        if self.client_data != None:
            self.model.run_engine._client.logout()

    def loginUser(self, isLogged):
        re = self.model.run_engine
        if isLogged:
            username = self.login._email.text()
            password = self.login._password.text()
            self.client_data = re._client.login(
                username=username, password=password,
                provider='ldap/token')
            re._client.apikey_new(expires_in=3600)
            re._user_name = username
            re._user_group = self.login._allowed_group
            self.login._email.setText("")
            self.login._password.setText("")
        else:
            re._user_name = 'GUI Client'
            re._user_group = 'primary'
            re._client.logout()
            self.client_data = None

    # def _process_new_console_output(self, res):
    #     self.lbl.setText(res)

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


        vsplitter = QSplitter(Qt.Vertical)

        hsplitter = QSplitter(Qt.Horizontal)
        queue = SophysQueueTable(self.model)
        hsplitter.addWidget(queue)

        running = SophysRunningItem(self.model)
        hsplitter.addWidget(running)

        history = SophysHistoryTable(self.model)
        hsplitter.addWidget(history)

        hsplitter.setSizes([500, 100, 500])
        vsplitter.addWidget(hsplitter)

        live_view = LiveView('TEST_BL_bluesky', '127.0.0.1:kakfa_port')
        vsplitter.addWidget(live_view)

        glay.addWidget(vsplitter, 1, 0, 1, 3)
        # self.model.run_engine.start_console_output_monitoring()
        # self.lbl = QLabel()
        # self.model.run_engine.console_monitoring_thread.returned.connect(self._process_new_console_output)

        self.setCentralWidget(wid)
