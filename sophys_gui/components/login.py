from qtpy.QtWidgets import QApplication
from suitscase import LoginCNPEM
from sophys_gui.functions import addLineJumps


class SophysLogin(LoginCNPEM):

    def __init__(self, model):
        super().__init__()
        self.runEngine = model.run_engine
        self.app = QApplication.instance()
        self.login_signal.connect(self.handleToggleUser)
        self._email.setMinimumWidth(150)
        self._password.setMinimumWidth(150)
        tooltip_msg = "Login into the HTTP Server in order to be " \
            "able to control and operate the Queue Server. Without the login " \
            "you will be on the observer mode."
        tooltip_msg = addLineJumps(tooltip_msg)
        self.setToolTip(tooltip_msg)

    def logoutUser(self):
        re = self.runEngine
        re._user_name = 'GUI Client'
        re._user_group = 'primary'
        re._client.logout()
        self.app.saveRunEngineClient(None)
        self.client_data = None

    def loginUser(self):
        re = self.runEngine
        emailWid = self._email
        passwordWid = self._password
        username = emailWid.text()
        password = passwordWid.text()
        self.client_data = re._client.login(
            username=username, password=password,
            provider="ldap/token")
        if self.client_data:
            self.app.saveRunEngineClient(re._client)
            re._user_name = username
            re._user_group = self._allowed_group
            emailWid.setText("")
            passwordWid.setText("")
        else:
            self.toggle_login_status()
            self.logoutUser()

    def handleToggleUser(self, isLogged):
        """
            Toggle user permissions.
        """
        if isLogged:
            self.loginUser()
            return
        self.logoutUser()