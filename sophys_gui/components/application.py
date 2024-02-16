import sys
import time
import signal
import json
import traceback
from qtpy.QtWidgets import QApplication, QMessageBox
from sophys_gui.functions import getFilePath
from .popup import PopupWidget


class SophysApplication(QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.popup = []
        self._setupUi()

    def setVariables(self, stylesheet):
        file = getFilePath("_assets/css-variables.json")
        variables = json.load(open(file))
        for key, value in variables.items():
            stylesheet = stylesheet.replace(key, value)
        return stylesheet

    def setStyle(self):
        """
            Generate a generic style for the applications.
        """
        style_file = getFilePath("_assets/css-style.css")
        with open(style_file, 'r') as f:
            style = f.read()
        style = self.setVariables(style)
        self.setStyleSheet(style)

    def showBugError(self, exctype, excvalue, tracebackobj):
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
        for popup in self.popup:
            if popup:
                popup.set_text(message)
                popup.show_popup()
            else:
                self.popup.pop(popup)

    def verifyKnownExceptions(self, excvalue):
        exception = str(excvalue)

        digitList = [x.isdigit() for x in exception]
        try:
            firstDigit = digitList.index(True)
            messageCode = exception[firstDigit:firstDigit+3]
            if "001"==messageCode:
                return "Invalid Input type!!"
            if "002"==messageCode:
                return "Missing required fields!!"
            if "401"==messageCode:
                return "Not enough permissions!!"
        except Exception:
            return ""
        return ""

    def excepthook(self, exctype, excvalue, tracebackobj):
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
