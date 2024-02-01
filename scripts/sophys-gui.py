#!/usr/bin/env python

import sys
import signal
import qtawesome

from qtpy.QtWidgets import QApplication

from sophys_gui.server import QueueServerModel
from sophys_gui.operation import SophysOperationGUI

signal.signal(signal.SIGINT, signal.SIG_DFL)

__backend_model = QueueServerModel()


app = QApplication(sys.argv)

window = SophysOperationGUI(__backend_model)
window.setWindowIcon(qtawesome.icon("mdi.cloud"))
window.show()

__backend_model.run_engine.load_re_manager_status(unbuffered=True)

ret = app.exec_()
__backend_model.exit()
sys.exit(ret)
