import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QPushButton, \
    QLabel, QGroupBox, QHBoxLayout, QApplication, QSizePolicy

from sophys_gui.functions import getHeader

from suitscase.utilities.threading import DeferredFunction


class SophysRunningItem(QWidget):

    def __init__(self, model):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.group = QGroupBox()
        self.model = model
        self.currThread = QApplication.instance().thread()
        self.model.run_engine.events.running_item_changed.connect(
            self.runningItemChanged)
        self._setupUi()

    def create_btns(self, glay, btn_dict):
        for idy, btn_dict in enumerate(btn_dict):
            title = btn_dict["title"]
            btn = QPushButton(title)
            btn.clicked.connect(btn_dict["cmd"])
            btn.setIcon(qta.icon(btn_dict["icon"]))
            glay.addWidget(btn, 6, idy, 1, 2)

    def setCommandButtons(self, model, glay):
        control_btns = [
            {
                "title": "Update Environment",
                "icon": "mdi6.update",
                "cmd": print
            }
        ]
        self.create_btns(glay, control_btns)

    def detectLoading(self, item):
        isVisible = False
        if len(item) > 0:
            isVisible = True
        self.loading.setVisible(isVisible)

    def runningItemChanged(self, evt):
        running_item = self.model.run_engine._running_item
        self.detectLoading(running_item)
        self.getItemAttributes(running_item)

    def createDictionaryWidget(self, arg_dict):
        widget = QWidget()
        lay = QGridLayout()
        widget.setLayout(lay)
        idx = 0
        isDict = isinstance(arg_dict, dict)
        key_list = arg_dict
        if isDict:
            key_list = list(arg_dict.keys())
        for key in key_list:
            title = QLabel(key)
            title.setStyleSheet("font-weight: 300;")
            lay.addWidget(title, idx, 0, 1, 1)

            if isDict:
                value = QLabel(str(arg_dict[key]))
                value.setWordWrap(True)
                value.setAlignment(Qt.AlignCenter)
                lay.addWidget(value, idx, 1, 1, 1)
            idx += 1

        return widget

    @DeferredFunction
    def getItemAttributes(self, running_item):
        args_list = ['kwargs', 'item_type', 'args', 'name']
        isArgsNull = False
        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)
        idx = 0
        idy = 0
        for key, item in running_item.items():
            if key in args_list:
                isArgs = key == 'args'
                item_group = QGroupBox()
                lay = QHBoxLayout()
                item_group.setLayout(lay)
                item_group.setTitle(key)
                col_stretch = 1
                if isArgs:
                    isArgsNull = len(item)==0
                    idy -=1
                if isArgsNull:
                    col_stretch = 2
                if key != 'args' or not isArgsNull:
                    glay.addWidget(item_group, idx, idy, 1, col_stretch)

                if isinstance(item, str):
                    value = QLabel(item)
                    value.setAlignment(Qt.AlignCenter)
                else:
                    value = self.createDictionaryWidget(item)
                lay.addWidget(value)

                idy += 1
                if idy >= 2:
                    idy = 0
                    idx += 2

        self.group.deleteLater()
        self.attributesDisplay.addWidget(group)
        self.group = group

    def getLoadingButton(self):
        self.loading = QPushButton('')
        self.loading.setIcon(qta.icon(
            'fa5s.spinner', animation=qta.Spin(self.loading)))
        self.loading.setVisible(False)
        self.loading.setFlat(True)

    def _setupUi(self):
        glay = QGridLayout(self)

        header = getHeader("Running")
        glay.addWidget(header, 0, 0, 1, 1)

        self.getLoadingButton()
        glay.addWidget(self.loading, 0, 1, 1, 1)

        self.attributesDisplay = QHBoxLayout()
        glay.addLayout(self.attributesDisplay, 1, 0, 5, 2)

        self.setCommandButtons(self.model, glay)
