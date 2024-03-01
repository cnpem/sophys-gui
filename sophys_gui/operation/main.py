from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow, QWidget, QSplitter, \
    QGridLayout, QTabWidget, QApplication
from sophys_gui.components import SophysQueueTable, \
    SophysHistoryTable, SophysRunningItem, QueueController, \
    SophysConsoleMonitor
from kafka_bluesky_live.live_view import LiveView, VisualElements
from suitscase import LoginCNPEM


class SophysOperationGUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.runEngine = self.model.run_engine
        self.app = QApplication.instance()
        self.client_data = None
        self._setupUi()

    def closeEvent(self, event):
        if self.client_data != None:
            self.logoutUser()
        self.runEngine.stop_console_output_monitoring()

    def logoutUser(self):
        re = self.runEngine
        re._user_name = 'GUI Client'
        re._user_group = 'primary'
        re._client.logout()
        self.app.saveRunEngineClient(None)
        self.client_data = None

    def loginUser(self):
        re = self.runEngine
        emailWid = self.login._email
        passwordWid = self.login._password
        username = emailWid.text()
        password = passwordWid.text()
        self.client_data = re._client.login(
            username=username, password=password,
            provider="ldap/token")
        self.app.saveRunEngineClient(re._client)
        re._user_name = username
        re._user_group = self.login._allowed_group
        emailWid.setText("")
        passwordWid.setText("")

    def handleToggleUser(self, isLogged):
        if isLogged:
            self.loginUser()
            return
        self.logoutUser()

    def createLoginWidget(self):
        login = LoginCNPEM(group="SWC")
        login.login_signal.connect(self.handleToggleUser)
        login._email.setMinimumWidth(150)
        login._password.setMinimumWidth(150)
        login.setToolTip("Login into the HTTP Server in order to be " \
            "able to control and operate the Queue Server. Without the login "
            "you will be on the observer mode.")
        return login

    def _setupUi(self):
        wid = QWidget()
        glay = QGridLayout()
        wid.setLayout(glay)

        self.login = self.createLoginWidget()
        self.login.setMaximumWidth(500)
        loginChanged = self.login.login_signal
        glay.addWidget(self.login, 0, 2, 1, 1)

        controller = QueueController(self.model, loginChanged)
        glay.addWidget(controller, 0, 0, 1, 2)


        vsplitter = QSplitter(Qt.Vertical)

        hsplitter = QSplitter(Qt.Horizontal)
        queue = SophysQueueTable(self.model, loginChanged)
        hsplitter.addWidget(queue)

        running = SophysRunningItem(self.model)
        hsplitter.addWidget(running)

        history = SophysHistoryTable(self.model, loginChanged)
        hsplitter.addWidget(history)

        hsplitter.setSizes([500, 100, 500])
        vsplitter.addWidget(hsplitter)

        resultTabs = QTabWidget()
        vsplitter.addWidget(resultTabs)

        visual_elements = VisualElements(cnpem_icon=None, lnls_icon=None, background_icon=None)
        live_view = LiveView('TEST_BL_bluesky', '127.0.0.1:kakfa_port', visual_elements)
        resultTabs.addTab(live_view, "Live View")

        console = SophysConsoleMonitor(self.model)
        resultTabs.addTab(console, "Console")

        vsplitter.setSizes([600, 200])
        glay.addWidget(vsplitter, 1, 0, 1, 3)

        self.setCentralWidget(wid)
