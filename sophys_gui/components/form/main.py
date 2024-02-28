import typing
import typesentry
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout, \
    QApplication
from sophys_gui.functions import evaluateValue
from ..input import SophysInputList, SophysInputDict, SophysSpinBox, \
    SophysInputMotor
from .util import UNKNOWN_TYPES

NoneType = type(None)


class SophysForm(QDialog):

    def __init__(self, model, modalMode, allowedParameters, allowedNames):
        super().__init__()
        self.allowedParameters = allowedParameters
        self.allowedNames = allowedNames
        self.inputWidgets = {}
        self.model = model
        self.modalMode = modalMode
        self.itemType = "instruction" if "instruction" in modalMode else "plan"
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
        selectedItem = self.model._selected_queue_item_uids
        itemPos = self.model.queue_item_uid_to_pos(selectedItem[0])
        return self.model._plan_queue_items[itemPos]

    def getHasParameters(self, value):
        hasParam = bool(value) and value != "None"
        if hasParam and isinstance(value, str):
            hasParam = len(value) > 0
        return hasParam

    def handleDetectorValue(self, inputWid, key):
        value = inputWid["widget"].text()
        isDetector = inputWid["kind"] == "POSITIONAL_ONLY" or key == "detectors"
        if isDetector and isinstance(value, str):
            value = [value]
        return value

    def verifyValueType(self, value, widType):
        try:
            return typesentry.Config().is_type(value, widType)
        except Exception:
            print(value, type(value), widType)
        return False

    def getItemParameters(self):
        inputValues = {
            "kwargs": {},
            "args": []
        }
        isValid = True
        for key, inputWid in self.inputWidgets.items():
            isRequired = inputWid["required"]
            value = self.handleDetectorValue(inputWid, key)
            hasParam = self.getHasParameters(value)
            if hasParam:
                value = evaluateValue(value)
                validParam = self.verifyValueType(value, inputWid["type"])
                if validParam:
                    isDetectors = inputWid["kind"] == "POSITIONAL_ONLY"
                    isMotors = inputWid["kind"] == "VAR_POSITIONAL"
                    if isMotors:
                        inputValues["args"].extend(value)
                    elif isDetectors:
                        inputValues["args"].append(value)
                    else:
                        inputValues["kwargs"][key] = value
                else:
                    isValid = False
                    exception = "001: Invalid Input type!!"
            elif isRequired:
                isValid = False
                exception = "002: Missing required fields!!"

        if not isValid:
            raise Exception(exception)
        return inputValues

    def getItemMetadata(self, itemParameters):
        metadata = {
            "item_type": self.itemType,
            "name": self.chosenItem,
            "user": self.model._user_name,
            "user_group": self.model._user_group
        }
        metadata = metadata | itemParameters
        hasUid = "edit" in self.modalMode
        if hasUid:
            metadata["item_uid"] = self.selectedItemMetadata()["item_uid"]
        return metadata

    def addItemToQueue(self):
        itemParameters = self.getItemParameters()
        item = self.getItemMetadata(itemParameters)
        isItemUpdate = "edit" in self.modalMode
        if isItemUpdate:
            self.model.queue_item_update(item=item)
        else:
            self.model.queue_item_add(item=item)
        self.accept()

    def getDialogBtns(self):
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.btns.accepted.connect(self.addItemToQueue)
        self.btns.rejected.connect(self.reject)

        return self.btns

    def setWidgetValue(self, inputWid, item, isStr):
        if isStr:
            inputWid.setText(str(item))
        else:
            inputWid.setValue(item)

    def addDefaultValues(self, paramMeta, inputWid):
        placeHolderType = any([isinstance(inputWid, widType) for widType in [QLineEdit, SophysSpinBox]])
        if placeHolderType:
            default = ""
            if "default" in paramMeta:
                default = paramMeta["default"]
            inputWid.setPlaceholderText(default)

    def handleArgsParam(self, argsParams, paramName):
        item = None
        isDetectors = paramName == "detectors"
        isMotors = paramName == "args"
        if isDetectors:
            item = argsParams[0]
        elif isMotors:
            argsParams = argsParams.copy()
            argsParams.pop(0)
            item = argsParams
        return item

    def handleModalMode(self, inputWid, paramMeta, isStr):
        isNotAdd = "add" not in self.modalMode
        if isNotAdd:
            paramName = paramMeta["name"]
            metadata = self.selectedItemMetadata()
            hasKwargs = "kwargs" in metadata
            hasArgs = "args" in metadata
            item = None
            if hasKwargs:
                kwargsParams = metadata["kwargs"]
                if paramName in kwargsParams:
                    item = kwargsParams[paramName]
            if hasArgs and not item:
                item = self.handleArgsParam(metadata["args"], paramName)
            if item:
                self.setWidgetValue(inputWid, item, isStr)

        self.addDefaultValues(paramMeta, inputWid)

    def getAvailableDevicesType(self, title):
        optionsMode = {
            "motor": "is_movable",
            "detectors": "is_readable",
            "flyers": "is_flyable"
        }
        return optionsMode[title] if title in optionsMode else None

    def getDevicesOptions(self, availableDevices):
        allowedDevices = self.model._allowed_devices
        optionsList = []
        for key, device in allowedDevices.items():
            if device[availableDevices]:
                optionsList.append(key)
        return optionsList

    def getIterableInput(self, paramMeta, isNumber, isGrouped=False):
        optionsList = None
        availableDevices = self.getAvailableDevicesType(paramMeta["name"])
        if availableDevices:
            optionsList = self.getDevicesOptions(availableDevices)
        return SophysInputList(optionsList, isNumber, not isGrouped)

    def getInputTooltip(self, param):
        hasDescription = "description" in param
        if hasDescription:
            description = param["description"]
            try:
                extraIdx = description.index("-.-")
                description = description[:extraIdx]
            except Exception:
                print("No Motor Separator")
            return description.capitalize()
        return ""

    def getInputWidget(self, paramMeta, paramType):
        isNumber = any([item in paramType for item in ["int", "float"]])
        isIterable = any([item in paramType for item in ["Iterable", "List", "object"]])
        isArgs = "args" in paramMeta["name"]
        isDict  = "dict" in paramType
        isStr = not (isNumber or isDict or isIterable)
        if isDict:
            inputWid = SophysInputDict()
        elif isArgs:
            inputWid = SophysInputMotor(paramMeta, self.getIterableInput)
        elif isIterable:
            inputWid = self.getIterableInput(paramMeta, isNumber)
        elif isNumber:
            numType = "int" if "int" in paramType else "float"
            inputWid = SophysSpinBox(numType)
            inputWid.setMaximumHeight(50)
        else:
            inputWid = QLineEdit()
        self.handleModalMode(inputWid, paramMeta, isStr)
        inputWid.setToolTip(self.getInputTooltip(paramMeta))
        return inputWid

    def getIsRequired(self, paramMeta, varType):
        hasDefaultValue = "default" in paramMeta
        return not (hasDefaultValue or "Optional" in varType)

    def replaceUnknownTypes(self, varType):
        for keyType, replaceType in UNKNOWN_TYPES.items():
            varType = varType.replace(keyType, replaceType)
        return varType

    def getParamPythonType(self, paramMeta):
        hasAnnotation = "annotation" in paramMeta
        varType = paramMeta["annotation"]["type"] if hasAnnotation else ""
        varType = self.replaceUnknownTypes(varType)
        return eval(varType) if varType != "" else object

    def getInputTitle(self, title, isRequired):
        reqText = " (required)" if isRequired else ""
        lbl = QLabel(title + reqText)
        lbl.setMaximumHeight(50)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def addParameterInput(self, paramMeta, pos, glay):
        paramType = self.getParamPythonType(paramMeta)
        isRequired = self.getIsRequired(paramMeta, str(paramType))

        title = paramMeta["name"]
        lbl = self.getInputTitle(title, isRequired)
        glay.addWidget(lbl, *pos, 1, 1)
        pos[0] += 1

        rowStretch = 1 if title != "md" else 6 - pos[0]
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

    def getNoParametersLabel(self):
        noParamLbl = "There are no configurable parameters " \
            f"for the choosen {self.itemType}."
        return QLabel(noParamLbl)

    def updateParametersLayout(self, newGroup):
        self.group.deleteLater()
        self.parametersLayout.addWidget(newGroup)
        self.group = newGroup

    def changeCurrentItem(self, currentItem):
        """
            Update the current plan input parameters.
        """
        itemAllowedParams = self.allowedParameters(name=currentItem)
        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)

        self.chosenItem = itemAllowedParams["name"]
        group.setTitle(self.chosenItem)

        hasParameters = "parameters" in itemAllowedParams
        if hasParameters:
            parameters = itemAllowedParams["parameters"]
            self.inputWidgets = {}
            pos = [0, 0]
            for paramMeta in parameters:
                pos = self.addParameterInput(paramMeta, pos, glay)
                if pos[0] > 4:
                    pos[0] = 0
                    pos[1] += 2

        else:
            glay.addWidget(self.getNoParametersLabel())
        self.updateParametersLayout(group)

    def getItemCombbox(self):
        """
            Create combobox for choosing the plan or instruction to add.
            Only appear when creating a new plan or instruction.
        """
        group = QGroupBox()
        group.setMaximumHeight(75)
        hlay = QHBoxLayout()
        group.setLayout(hlay)
        group.setTitle(self.itemType.capitalize())

        combobox = QComboBox()
        allowedNames = self.allowedNames()
        combobox.addItems(sorted(allowedNames))
        combobox.activated.connect(
            lambda idx, combobox=combobox: self.changeCurrentItem(combobox.itemText(idx)))
        currItem = combobox.itemText(0)
        hlay.addWidget(combobox)

        return group, currItem

    def setupUi(self):
        self.setMaximumSize(1000, 500)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.group = QGroupBox()
        self.parametersLayout = QGridLayout()
        lay = QVBoxLayout(self)

        isAddition = "add" in self.modalMode
        if isAddition:
            itemCombbox, currItem = self.getItemCombbox()
            lay.addWidget(itemCombbox)
        else:
            currItem = self.selectedItemMetadata()["name"]

        self.changeCurrentItem(currItem)
        lay.addLayout(self.parametersLayout)

        btns = self.getDialogBtns()
        lay.addWidget(btns)

        app = QApplication.instance()
        app.createPopup(self)
