import sys
import time
import signal
import json
import traceback
from qtpy.QtWidgets import QApplication, QMessageBox
from sophys_gui.functions import getFilePath


class SophysApplication(QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.configureApp()

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


    def excepthook(self, exctype, excvalue, tracebackobj):
        timestring = time.strftime("%Y-%m-%d, %H:%M:%S") + '\n'

        notice = timestring + \
            'An unhandled exception occurred. Please report the problem '\
            'via email to swc@lnls.br.'\

        errmsg = '{}: {}'.format(exctype.__name__, excvalue)+'\n\n'+\
                ''.join(traceback.format_tb(tracebackobj))

        errorbox = QMessageBox()
        errorbox.setText(notice)
        errorbox.setInformativeText(errmsg)
        errorbox.setIcon(QMessageBox.Critical)
        errorbox.setStyleSheet("text-align: center;")
        errorbox.setObjectName("ControlApp")
        errorbox.exec_()

    def configureApp(self):
        self.setStyle()
        sys.excepthook = self.excepthook
