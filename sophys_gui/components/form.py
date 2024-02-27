import typing
import typesentry
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout, \
    QApplication
from sophys_gui.functions import evaluateValue
from .input import SophysInputList, SophysInputDict, SophysSpinBox, \
    SophysInputMotor

NoneType = type(None)


class SophysForm(QDialog):

    def __init__(self, model, modalMode, allowed_parameters, allowed_names):
        super().__init__()
        self.allowed_parameters = allowed_parameters
        self.allowed_names = allowed_names
        self.inputWidgets = {}
        self.model = model
        self.modalMode = modalMode
        self.item_type = 'instruction' if 'instruction' in modalMode else 'plan'
        self.group = QGroupBox()
        self.planParameters = QGridLayout()
        self.setMaximumSize(1000, 500)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setupUi()

    def keyPressEvent(self: QDialog, event: object) -> None:
        """
            Override close dialog on pressing the Enter key.
        """
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            event.accept()
        else:
            super(SophysForm, self).keyPressEvent(event)

    def selectedItemMetadata(self):
        sel_item = self.model._selected_queue_item_uids
        pos = self.model.queue_item_uid_to_pos(sel_item[0])
        return self.model._plan_queue_items[pos]

    def getPlanParameters(self):
        inputValues = {
            'kwargs': {},
            'args': []
        }
        isValid = True
        for key, inputWid in self.inputWidgets.items():
            validParam = False
            hasParam = True
            value = inputWid["widget"].text()
            if inputWid["kind"] == "POSITIONAL_ONLY" or key == "detectors":
                if isinstance(value, str):
                    value = [value]
            hasParam = bool(value) and value != 'None'
            if hasParam and isinstance(value, str):
                hasParam = len(value) > 0
            if hasParam:
                value = evaluateValue(value)
                try:
                    validParam = typesentry.Config().is_type(value, inputWid['type'])
                except Exception:
                    print(value, type(value), inputWid['type'])
                if validParam:
                    if inputWid["kind"] == "VAR_POSITIONAL":
                        inputValues["args"].extend(value)
                    elif inputWid["kind"] == "POSITIONAL_ONLY":
                        inputValues["args"].append(value)
                    else:
                        inputValues["kwargs"][key] = value
                else:
                    isValid = False
                    exception = "001: Invalid Input type!!"
            elif inputWid["required"]:
                isValid = False
                exception = "002: Missing required fields!!"

        if not isValid:
            raise Exception(exception)
        return inputValues

    def getPlanMetadata(self, plan_parameters):
        metadata = {
            'item_type': self.item_type,
            'name': self.chosenItem,
            'user': self.model._user_name,
            'user_group': self.model._user_group
        }
        if self.item_type == "plan":
            metadata = metadata | plan_parameters
        if "edit" in self.modalMode:
            metadata['item_uid'] = self.selectedItemMetadata()["item_uid"]
        return metadata

    def addPlanToQueue(self):
        plan_parameters = self.getPlanParameters()
        item = self.getPlanMetadata(plan_parameters)
        if "edit" in self.modalMode:
            self.model.queue_item_update(item=item)
        else:
            self.model.queue_item_add(item=item)
        self.accept()

    def getDialogBtns(self):
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.btns.accepted.connect(self.addPlanToQueue)
        self.btns.rejected.connect(self.reject)

        return self.btns

    def setWidgetValue(self, inputWid, item, isStr):
        if isStr:
            inputWid.setText(str(item))
        else:
            inputWid.setValue(item)

    def handleModalMode(self, inputWid, paramMeta, isStr):
        if "add" not in self.modalMode:
            paramName = paramMeta["name"]
            metadata = self.selectedItemMetadata()
            if "kwargs" in metadata:
                kwargsParams = metadata["kwargs"]
                if paramName in kwargsParams:
                    item = kwargsParams[paramName]
                    self.setWidgetValue(inputWid, item, isStr)
                    return
            if "args" in metadata:
                argsParams = metadata["args"]
                if paramName == "detectors":
                    item = argsParams[0]
                    self.setWidgetValue(inputWid, item, isStr)
                    return
                elif paramName == "args":
                    argsParams = argsParams.copy()
                    argsParams.pop(0)
                    item = argsParams
                    self.setWidgetValue(inputWid, item, isStr)
                    return
        if isinstance(inputWid, QLineEdit) or isinstance(inputWid, SophysSpinBox):
            default = ''
            if "default" in paramMeta:
                default = paramMeta["default"]
            inputWid.setPlaceholderText(default)

    def getIterableInput(self, paramMeta, isFloat, isGrouped=False):
        optionsList = None
        title = paramMeta["name"]
        isDevice = "is_movable" if "motor" == title else \
            "is_readable" if "detectors" in title else None
        allowed_devices = self.model._allowed_devices
        if isDevice:
            optionsList = []
            for key, device in allowed_devices.items():
                if device[isDevice]:
                    optionsList.append(key)
        return SophysInputList(optionsList, isFloat, not isGrouped)

    def getInputWidget(self, paramMeta, paramType):
        isInt = 'int' in paramType
        isFloat = 'float' in paramType
        isIterable = 'Iterable' in paramType or 'List' in paramType or 'object' in paramType
        isArgs = 'args' in paramMeta['name']
        isDict  = 'dict' in paramType
        if isDict:
            inputWid = SophysInputDict()
        elif isArgs:
            inputWid = SophysInputMotor(paramMeta, self.getIterableInput)
        elif isIterable:
            inputWid = self.getIterableInput(paramMeta, isFloat)
        elif isInt or isFloat:
            numType = 'int' if isInt else 'float'
            inputWid = SophysSpinBox(numType)
            inputWid.setMaximumHeight(50)
        else:
            inputWid = QLineEdit()
        isStr = not (isInt or isFloat or isDict or isIterable)
        self.handleModalMode(inputWid, paramMeta, isStr)

        return inputWid

    def isRequired(self, paramMeta, varType):
        hasDefaultValue = "default" in paramMeta
        return not (hasDefaultValue or "Optional" in varType)

    def addParameterInput(self, paramMeta, pos, glay):
        varType = paramMeta['annotation']['type'] if 'annotation' in paramMeta else ''
        varType = varType.replace('typing.Sequence', 'typing.List')
        varType = varType.replace('__READABLE__', 'typing.Any')
        varType = varType.replace('__DEVICE__', 'typing.Any')
        varType = varType.replace('__CALLABLE__', 'typing.Any')
        varType = varType.replace('__MOVABLE__', 'typing.Any')
        varType = varType.replace('__FLYABLE__', 'typing.Any')
        paramType = eval(varType) if varType != '' else object

        isRequired = self.isRequired(paramMeta, varType)

        title = paramMeta["name"]
        reqText = ' (required)' if isRequired else ''
        lbl = QLabel(title + reqText)
        lbl.setMaximumHeight(50)
        lbl.setAlignment(Qt.AlignCenter)
        glay.addWidget(lbl, *pos, 1, 1)
        pos[0] += 1

        rowStretch = 1
        if title == 'md':
            rowStretch = 6 - pos[0]
        inputWid = self.getInputWidget(paramMeta, str(paramType))
        glay.addWidget(inputWid, *pos, rowStretch, 1)
        pos[0] += 1

        self.inputWidgets[title] = {
            "widget": inputWid,
            "required": isRequired,
            "type": paramType,
            "kind": paramMeta["kind"]["name"]
        }

        return pos

    def changePlan(self, currentPlan):
        allowed_params = self.allowed_parameters(name=currentPlan)
        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)
        self.setChosenItem(allowed_params["name"])
        group.setTitle(self.chosenItem)
        if "parameters" in allowed_params:
            parameters = allowed_params["parameters"]
            self.inputWidgets = {}

            pos = [0, 0]
            for paramMeta in parameters:
                pos = self.addParameterInput(paramMeta, pos, glay)
                if pos[0] > 4:
                    pos[0] = 0
                    pos[1] += 2

        else:
            noParamLbl = "There are no configurable parameters " \
                f"for the choosen {self.item_type}."
            glay.addWidget(QLabel(noParamLbl))
        self.group.deleteLater()
        self.planParameters.addWidget(group)
        self.group = group

    def setChosenItem(self, itemName):
        self.chosenItem = itemName

    def changeCurrentPlan(self):
        group = QGroupBox()
        group.setMaximumHeight(75)
        hlay = QHBoxLayout()
        group.setLayout(hlay)
        group.setTitle("Plan")

        cb = QComboBox()
        allowedPlans = self.allowed_names()
        cb.addItems(sorted(allowedPlans))
        cb.activated.connect(lambda idx, cb=cb: self.changePlan(cb.itemText(idx)))
        self.changePlan(cb.itemText(0))
        hlay.addWidget(cb)

        return group

    def setupUi(self):
        lay = QVBoxLayout(self)

        if 'add' in self.modalMode:
            planCb = self.changeCurrentPlan()
            lay.addWidget(planCb)
        else:
            self.changePlan(self.selectedItemMetadata()['name'])

        lay.addLayout(self.planParameters)

        btns = self.getDialogBtns()
        lay.addWidget(btns)

        app = QApplication.instance()
        app.createPopup(self)
