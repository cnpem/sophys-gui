#!/usr/bin/env python

import sys
import qtawesome
from sophys_gui.server import ServerModel
from sophys_gui.components import SophysApplication
from sophys_gui.operation import SophysOperationGUI


__backend_model = ServerModel()

app = SophysApplication(sys.argv)

window = SophysOperationGUI(__backend_model)
window.setWindowIcon(qtawesome.icon("mdi.cloud", color="#ffffff"))
window.setWindowTitle("SOPHYS GUI")
window.show()
app.createPopup(window)

__backend_model.run_engine.load_re_manager_status(unbuffered=True)

ret = app.exec_()
__backend_model.exit()
sys.exit(ret)
