import yaml
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, \
    QLabel, QGroupBox, QHBoxLayout, QSizePolicy
from sophys_gui.functions import getHeader, createSingleBtn, \
    addArgsToKwargs, openYaml
from ..led import SophysLed
from .util import CONTROL_BTNS
from .progress import ProgressBar

from suitscase.utilities.threading import DeferredFunction


class SophysRunningItem(QWidget):
    """
        Widget that displays the parameters of the current running item.

        .. note::
            A loading icon will appear if the process is running.

        .. image:: ./_static/running.png
            :width: 300
            :alt: Running Item Widget
            :align: center

    """

    def __init__(self, model, loginChanged, kafka_bootstrap, kafka_topic, yml_file_path = None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.group = QGroupBox()
        self.runEngine = model.run_engine
        self.yml_file_path = yml_file_path
        self.config = openYaml(self.yml_file_path)
        self._setupUi(loginChanged, kafka_bootstrap, kafka_topic)

    def createBtns(self, glay, loginChanged):
        """
            Create all the buttons associated with the operation of the running item.
        """
        for idy, btnValue in enumerate(CONTROL_BTNS):
            btn = createSingleBtn(btnValue, self.runEngine)
            btn.setEnabled(False)
            loginChanged.connect(btn.setEnabled)
            glay.addWidget(btn, 7, idy, 1, 2)

    def newKwargsName(self, key, runningItem):

        name = runningItem.get("name", "")
        plan_configuration = self.config.get(name, {})
        parameters_dict = plan_configuration.get("param_names", {})

        kwargs_dict = dict()

        if isinstance(parameters_dict, dict):

            for value in parameters_dict.values():

                if isinstance(value, dict):
                    kwargs_dict.update(value)
            
                else:
                    kwargs_dict.update(parameters_dict)
                    break

        return kwargs_dict.get(key, key)
            

    def createDictionaryWidget(self, arg_dict, runningItem):
        """
            Create a widget that displays a dictionary.
        """
        widget = QWidget()
        lay = QGridLayout()
        widget.setLayout(lay)
        idx = 0
        key_list = list(arg_dict.keys())
        for key in key_list:

            new_key = key

            if self.yml_file_path:
                new_key = self.newKwargsName(key, runningItem)

            title = QLabel(new_key)
            title.setStyleSheet("font-weight: 300;")
            lay.addWidget(title, idx, 0, 1, 1)

            value = QLabel(str(arg_dict[key]))
            value.setWordWrap(True)
            value.setAlignment(Qt.AlignCenter)
            lay.addWidget(value, idx, 1, 1, 1)
            idx += 1

        return widget

    def updateRunningItem(self, group):
        """
            Update running item widget.
        """
        self.group.deleteLater()
        self.attributesDisplay.addWidget(group)
        self.group = group

    def handleArgsList(self, runningItem):
        """
            Append the args into the kwargs dictionary.
        """
        if not "kwargs" in runningItem:
            runningItem["kwargs"] = {}
        if "args" in runningItem:
            hasArgs = len(runningItem["args"]) != 0
            if hasArgs:
                argsList = [
                    runningItem["args"], runningItem["kwargs"]
                ]
                addArgsToKwargs(argsList)
        return runningItem["kwargs"]

    def getValueWidget(self, runningItem, key):
        """
            Create the widget for showing the key value.
        """
        item = {}
        if key in runningItem:

            if key == 'name':
                plan_name = runningItem[key]
                item = self.config.get(plan_name, {}).get("name", plan_name)
            else:
                item = runningItem[key]
        if isinstance(item, str):
            value = QLabel(item)
            value.setAlignment(Qt.AlignCenter)
        else:
            argsDict = self.handleArgsList(runningItem)
            value = self.createDictionaryWidget(argsDict, runningItem)
        return value


    @DeferredFunction
    def updateRunningItemWidget(self, evt):
        """
            Update the widget showing the current running item.
        """
        args_list = ["user", "name", "kwargs"]
        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)
        runningItem = self.runEngine._running_item
        hasRunningItem = len(runningItem) != 0
        if hasRunningItem:
            pos = [0, 0]
            for key in args_list:
                item_group = QGroupBox()
                lay = QHBoxLayout()
                item_group.setLayout(lay)
                item_group.setTitle(key)
                stretch = 2 if key == "kwargs" else 1
                glay.addWidget(item_group, *pos, 1, stretch)

                valueWid = self.getValueWidget(runningItem, key)
                lay.addWidget(valueWid)

                pos[1] += 1
                if pos[1] >= 2:
                    pos[1] = 0
                    pos[0] += 2
        self.updateRunningItem(group)

    def createLoading(self):
        """
            Create loading icon to indicate if the queue is running.
        """
        statusComp = lambda stateVar: stateVar == "executing_queue"
        statusKey = "manager_state"
        return SophysLed(
            self.runEngine, statusKey, statusComp, isLoading=True)

    def _setupUi(self, loginChanged, kafka_bootstrap, kafka_topic):
        glay = QGridLayout(self)

        header = getHeader("Running")
        glay.addWidget(header, 0, 0, 1, 1)

        loading = self.createLoading()
        glay.addWidget(loading, 0, 1, 1, 1)

        progressBar = ProgressBar(self.runEngine, kafka_bootstrap, kafka_topic)
        progressBar.setOrientation(Qt.Horizontal)
        glay.addWidget(progressBar, 1, 0, 1, 2)

        self.attributesDisplay = QHBoxLayout()
        self.attributesDisplay.addWidget(self.group)
        glay.addLayout(self.attributesDisplay, 2, 0, 5, 2)

        self.createBtns(glay, loginChanged)

        self.runEngine.events.running_item_changed.connect(
            self.updateRunningItemWidget)
