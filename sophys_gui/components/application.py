import sys
import time
import signal
import traceback
from qtpy.QtWidgets import QApplication, QMessageBox
from sophys_gui.functions import getFilePath
from .popup import PopupWidget


class SophysApplication(QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        self.popup = []
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

    def showBugError(self, exctype, excvalue, tracebackobj):
        """
            Show a new window for unknown errors.
        """
        timestring = time.strftime("%Y-%m-%d, %H:%M:%S") + '\n'
        notice = timestring + \
            'An unhandled exception occurred. Please report the problem '\
            'via email to swc@lnls.br.'
        errmsg = '{}: {}'.format(exctype.__name__, excvalue)+'\n\n'+\
                ''.join(traceback.format_tb(tracebackobj))
        errorbox = QMessageBox()
        errorbox.setText(notice)
        errorbox.setInformativeText(errmsg)
        errorbox.setIcon(QMessageBox.Critical)
        errorbox.setStyleSheet("text-align: center;")
        errorbox.setObjectName("ControlApp")
        errorbox.exec_()

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
        for code, errorMsg in self.codeErrors.items():
            if code == messageCode:
                return errorMsg
        return ""

    def excepthook(self, exctype, excvalue, tracebackobj):
        """
            Catch thrown exceptions.
        """
        message = self.verifyKnownExceptions(excvalue)
        if self.popup and len(message)>0:
            self.showExpectedError(message)
        else:
            self.showBugError(exctype, excvalue, tracebackobj)

    def createPopup(self, window):
        popup = PopupWidget(window)
        popup.setVisible(False)
        self.popup.append(popup)

    def _setupUi(self):
        self.setStyle()
        sys.excepthook = self.excepthook
        signal.signal(signal.SIGINT, signal.SIG_DFL)
