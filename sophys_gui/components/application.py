import signal
import sys
import time
import traceback
from types import TracebackType

from qtpy.QtWidgets import QApplication, QMessageBox, QTextEdit

from sophys_gui.functions import getFilePath

from .popup import PopupWidget


class ResizableMessageBox(QMessageBox):
    def __init__(self, max_width: int, max_height: int, *, parent=None):
        super().__init__(parent=parent)

        self.max_width = max_width
        self.max_height = max_height

        self._override_max_size()

    def _override_max_size(self):
        self.setMaximumWidth(self.max_width)
        self.setMaximumHeight(self.max_height)

        text_edit = self.findChild(QTextEdit)
        if text_edit is not None:
            text_edit.setMaximumWidth(16777215)
            text_edit.setMaximumHeight(16777215)

    def event(self, event):
        res = super().event(event)
        self._override_max_size()
        return res


class SophysApplication(QApplication):
    """
        Application that enables generic utilities for the widgets.

        Features enabled:
            * Error Window
            * Popup
            * Styling

    """

    def __init__(self, argv, use_stylesheet = True):
        super().__init__(argv)
        self.popup = []
        self.runEngineClient = None
        self.use_stylesheet = use_stylesheet
        self.codeErrors = {
            "001": "Invalid Input type!!",
            "002": "Missing required fields!!",
            "401": "Not enough permissions!!"
        }
        self._setupUi()

    def setStyle(self):
        """
            Generate a generic style for the GUI application.
        """
        style_file = getFilePath("_assets/css-style.css")
        with open(style_file, 'r') as f:
            style = f.read()
        self.setStyleSheet(style)

    def showBugError(self, exctype: type[BaseException], excvalue: BaseException, tracebackobj: TracebackType):
        """
            Show a new window for unknown errors.
        """
        timestring = time.strftime("%Y-%m-%d, %H:%M:%S")
        notice = (
            timestring
            + "\n"
            + "An unhandled exception occurred. Please report the problem via email to swc@lnls.br."
        )

        exception_msg = "".join(traceback.format_exception(exctype, value=excvalue, tb=tracebackobj))

        errorbox = ResizableMessageBox(1200, 1200)
        errorbox.setText(notice)
        errorbox.setDetailedText(exception_msg)
        errorbox.setIcon(QMessageBox.Critical)
        errorbox.setSizeGripEnabled(True)
        errorbox.setObjectName("ControlApp")
        errorbox.exec()

    def showExpectedError(self, message):
        """
            Show a popup for user known errors.
        """
        for popup in self.popup:
            if popup:
                popup.set_text(message)
                popup.show_popup()
            else:
                self.popup.pop(popup)

    def getErrorCode(self, exception):
        """
            Get error code from the exception message.
        """
        digitList = [x.isdigit() for x in exception]
        try:
            firstDigit = digitList.index(True)
            return exception[firstDigit:firstDigit+3]
        except Exception:
            return ""

    def verifyKnownExceptions(self, excvalue):
        """
            Verify known error dictionary.
        """
        exception = str(excvalue)
        messageCode = self.getErrorCode(exception)
        if messageCode == "401" and self.runEngineClient:
                authKeys = self.runEngineClient.auth_key
                try:
                    clientData = self.runEngineClient.session_refresh(refresh_token=authKeys[1])
                    self.saveRunEngineClient(clientData["refresh_token"])
                    return "User Session Refreshed!!"
                except Exception:
                    print("Could not refresh the user session!")
        for code, errorMsg in self.codeErrors.items():
            if code == messageCode:
                return errorMsg
        return ""

    def excepthook(self, exctype: type, excvalue: BaseException, tracebackobj: TracebackType):
        """
            Catch thrown exceptions.
        """
        message = self.verifyKnownExceptions(excvalue)
        if self.popup and len(message)>0:
            self.showExpectedError(message)
        else:
            self.showBugError(exctype, excvalue, tracebackobj)

    def createPopup(self, window):
        """
            Create a hidden popup widget.
        """
        if isinstance(self.popup, list):
            popup = PopupWidget(window)
            popup.setVisible(False)
            popup.setStyleSheet("""
                margin: 1em;
                background-color: #ffdb3b;
                border: 1px solid #808080;
                border-radius: 10px;
            """)
            self.popup.append(popup)

    def saveRunEngineClient(self, client):
        self.runEngineClient = client

    def _setupUi(self):
        if self.use_stylesheet:
            self.setStyle()
        sys.excepthook = self.excepthook
        signal.signal(signal.SIGINT, signal.SIG_DFL)
