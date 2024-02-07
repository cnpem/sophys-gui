#!/usr/bin/env python

import sys
import signal
import qtawesome
import json
from qtpy.QtWidgets import QApplication

from sophys_gui.server import QueueServerModel
from sophys_gui.operation import SophysOperationGUI
from sophys_gui.functions import getFilePath

def setVariables(stylesheet):
    file = getFilePath("_assets/css-variables.json")
    variables = json.load(open(file))
    for key, value in variables.items():
        stylesheet = stylesheet.replace(key, value)
    return stylesheet

def setStyle(app):
    """
        Generate a generic style for the applications.
    """
    style_file = getFilePath("_assets/css-style.css")
    with open(style_file, 'r') as f:
        style = f.read()
    style = setVariables(style)
    app.setStyleSheet(style)

signal.signal(signal.SIGINT, signal.SIG_DFL)

__backend_model = QueueServerModel()


app = QApplication(sys.argv)
setStyle(app)

window = SophysOperationGUI(__backend_model)
window.setWindowIcon(qtawesome.icon("mdi.cloud", color="#ffffff"))
window.setWindowTitle("SOPHYS GUI")
window.show()

__backend_model.run_engine.load_re_manager_status(unbuffered=True)

ret = app.exec_()
__backend_model.exit()
sys.exit(ret)
