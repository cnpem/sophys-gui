#!/usr/bin/env python

import sys
import signal
from qtpy.QtWidgets import QApplication, QTableView

from src.server import QueueServerModel
from src.components import QueueModel

signal.signal(signal.SIGINT, signal.SIG_DFL)


__backend_model = QueueServerModel()

model = QueueModel(__backend_model)

app = QApplication(sys.argv)

view = QTableView()
view.horizontalHeader().setStretchLastSection(True)
view.setModel(model)

view.show()

__backend_model.run_engine.load_re_manager_status(unbuffered=True)

ret = app.exec_()
__backend_model.exit()
sys.exit(ret)
