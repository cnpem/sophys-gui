from enum import IntEnum

from qtpy.QtCore import QSize, Qt, Signal, Slot
from qtpy.QtGui import QFont, QShortcut, QKeySequence
from qtpy.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QStackedWidget,
    QLabel,
    QGridLayout,
    QPushButton,
    QToolButton,
    QWidgetAction,
    QHBoxLayout,
)

import qtawesome as qta

from sophys_gui.functions import addLineJumps


class SophysLogin(QWidget):
    login_status_changed = Signal(bool)  # is currently logged in

    class ButtonsConfiguration(IntEnum):
        LOGGED_OFF = 0
        LOADING = 1
        LOGGED_IN = 2

    def __init__(self, run_engine):
        super().__init__()

        self._run_engine = run_engine
        self._app = QApplication.instance()

        tooltip_msg = (
            "Login into the HTTP Server in order to be "
            "able to control and operate the Queue Server. Without the login "
            "you will be on the observer mode."
        )
        tooltip_msg = addLineJumps(tooltip_msg)
        self.setToolTip(tooltip_msg)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self._info_message = QLabel("Anonymous User")
        self._info_message.setStyleSheet(
            """
            background-color:00000000;"""
        )
        self._info_message.setAlignment(Qt.AlignCenter)
        self._info_message.setFont(QFont("Times", 15))

        layout.addWidget(self._info_message, 4)

        self._buttons_widget = QStackedWidget()

        credentials_form = QWidget()
        credentials_layout = QGridLayout()
        credentials_form.setLayout(credentials_layout)

        _ = QLabel("Email/Username:")
        self._email_line_edit = QLineEdit()
        self._email_line_edit.returnPressed.connect(self.attempt_login)
        self._email_line_edit.setMinimumWidth(150)

        credentials_layout.addWidget(_, 1, 0, 1, 1)
        credentials_layout.addWidget(self._email_line_edit, 1, 1, 1, 1)

        _ = QLabel("Password:")
        self._password_line_edit = QLineEdit()
        self._password_line_edit.returnPressed.connect(self.attempt_login)
        self._password_line_edit.setEchoMode(QLineEdit.Password)
        self._password_line_edit.setMinimumWidth(150)

        credentials_layout.addWidget(_, 2, 0, 1, 1)
        credentials_layout.addWidget(self._password_line_edit, 2, 1, 1, 1)

        login_button = QPushButton("Login")
        login_button.setDefault(True)
        login_button.clicked.connect(self.attempt_login)

        credentials_layout.addWidget(login_button, 3, 0, 1, 2)
        QShortcut(QKeySequence(Qt.Key_Tab), credentials_form, activated=self.change_focus)

        logged_out_button = QToolButton()
        logged_out_button_icon = qta.icon("ri.login-circle-line")
        logged_out_button.setIconSize(QSize(30, 30))
        logged_out_button.setIcon(logged_out_button_icon)
        logged_out_button.setPopupMode(QToolButton.InstantPopup)

        logged_out_button_action = QWidgetAction(logged_out_button)
        logged_out_button_action.setDefaultWidget(credentials_form)
        logged_out_button.addAction(logged_out_button_action)

        loading_button = QPushButton()
        loading_button.setIcon(
            qta.icon("fa5s.spinner", animation=qta.Spin(loading_button))
        )

        logged_in_button = QPushButton()
        logged_in_button_icon = qta.icon("ri.logout-circle-line")
        logged_in_button.setIconSize(QSize(30, 30))
        logged_in_button.setIcon(logged_in_button_icon)
        logged_in_button.clicked.connect(self.logout)

        _ = self._buttons_widget.addWidget(logged_out_button)
        assert _ == self.ButtonsConfiguration.LOGGED_OFF
        _ = self._buttons_widget.addWidget(loading_button)
        assert _ == self.ButtonsConfiguration.LOADING
        _ = self._buttons_widget.addWidget(logged_in_button)
        assert _ == self.ButtonsConfiguration.LOGGED_IN
        self._buttons_widget.setCurrentIndex(self.ButtonsConfiguration.LOGGED_OFF)

        layout.addWidget(self._buttons_widget, 1)

        self.setMaximumHeight(75)

    def change_focus(self):
        if self._email_line_edit.hasFocus():
            self._password_line_edit.setFocus(True)
        else:
            self._email_line_edit.setFocus(True)

    @Slot()
    def attempt_login(self):
        re = self._run_engine

        user_name = self._email_line_edit.text()
        password = self._password_line_edit.text()

        if "@" in user_name:
            user_name = user_name.split("@")[0]

        self._buttons_widget.setCurrentIndex(self.ButtonsConfiguration.LOADING)

        _exc = None
        try:
            response = re._client.login(
                username=user_name, password=password, provider="ldap/token"
            )
        except Exception as exc:
            print(f"Failed to login to httpserver: {exc}")
            _exc = exc

        if _exc is not None or response is None:
            self.logout()

            if _exc is not None:
                raise _exc

            return

        self._app.saveRunEngineClient(re._client)

        re._user_name = user_name
        re._user_group = None

        self._email_line_edit.setText("")
        self._password_line_edit.setText("")

        re._client.permissions_reload()

        self._info_message.setText(user_name)
        self._buttons_widget.setCurrentIndex(self.ButtonsConfiguration.LOGGED_IN)
        self.login_status_changed.emit(True)

    @Slot()
    def logout(self):
        self._buttons_widget.setCurrentIndex(self.ButtonsConfiguration.LOGGED_OFF)
        self._info_message.setText("Anonymous User")
        self.login_status_changed.emit(False)

        re = self._run_engine

        re._user_name = "GUI Client"
        re._user_group = "primary"

        self._app.saveRunEngineClient(None)

        re._client.logout()
