from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, \
    QLabel, QGroupBox, QHBoxLayout, QSizePolicy
from sophys_gui.functions import getHeader, createSingleBtn, \
    addArgsToKwargs
from ..led import SophysLed
from .util import CONTROL_BTNS

from suitscase.utilities.threading import DeferredFunction


class SophysRunningItem(QWidget):

    def __init__(self, model):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.group = QGroupBox()
        self.runEngine = model.run_engine
        self._setupUi()

    def createBtns(self, glay):
        """
            Create all the buttons associated with the operation of the running item.
        """
        for idy, btnValue in enumerate(CONTROL_BTNS):
            btn = createSingleBtn(btnValue, self.runEngine)
            glay.addWidget(btn, 6, idy, 1, 2)

    def runningItemChanged(self, evt):
        runningItem = self.runEngine._running_item
        self.getItemAttributes(runningItem)

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
    def getItemAttributes(self, runningItem):
        args_list = ['kwargs', 'user', 'name']
        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)
        idx = 0
        idy = 0
        for key, item in runningItem.items():
            if key in args_list:
                item_group = QGroupBox()
                lay = QHBoxLayout()
                item_group.setLayout(lay)
                item_group.setTitle(key)
                stretch = 2 if key == "kwargs" else 1
                glay.addWidget(item_group, idx, idy, 1, stretch)

                if isinstance(item, str):
                    value = QLabel(item)
                    value.setAlignment(Qt.AlignCenter)
                else:
                    argsList = [
                        runningItem["args"], runningItem["kwargs"]
                    ]
                    if len(argsList[0]) > 0:
                        addArgsToKwargs(argsList)
                    value = self.createDictionaryWidget(argsList[1])
                lay.addWidget(value)

                idy += 1
                if idy >= 2:
                    idy = 0
                    idx += 2

        self.group.deleteLater()
        self.attributesDisplay.addWidget(group)
        self.group = group

    def createLoading(self):
        statusComp = lambda stateVar: stateVar == "executing_queue"
        statusKey = "manager_state"
        return SophysLed(
            self.runEngine, statusKey, statusComp, isLoading=True)

    def _setupUi(self):
        glay = QGridLayout(self)

        header = getHeader("Running")
        glay.addWidget(header, 0, 0, 1, 1)

        loading = self.createLoading()
        glay.addWidget(loading, 0, 1, 1, 1)

        self.attributesDisplay = QHBoxLayout()
        self.attributesDisplay.addWidget(self.group)
        glay.addLayout(self.attributesDisplay, 1, 0, 5, 2)

        self.createBtns(glay)

        self.runEngine.events.running_item_changed.connect(
            self.runningItemChanged)
