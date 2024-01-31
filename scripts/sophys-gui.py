#!/usr/bin/env python

import sys
import signal
from qtpy.QtWidgets import QApplication

from sophys_gui.server import QueueServerModel
from sophys_gui.components import QueueModel, \
    SophysQueueTable

signal.signal(signal.SIGINT, signal.SIG_DFL)

__backend_model = QueueServerModel()

model = QueueModel(__backend_model)

app = QApplication(sys.argv)

view = SophysQueueTable(model, __backend_model)
view.show()

__backend_model.run_engine.load_re_manager_status(unbuffered=True)

ret = app.exec_()
__backend_model.exit()
sys.exit(ret)
