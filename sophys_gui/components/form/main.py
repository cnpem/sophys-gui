import typing
import typesentry
from math import floor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout, \
    QApplication, QCompleter
from sophys_gui.functions import evaluateValue, getMotorInput, addLineJumps
from ..input import SophysInputList, SophysInputDict, SophysSpinBox, \
    SophysInputMotor
from .util import UNKNOWN_TYPES

NoneType = type(None)


class SophysForm(QDialog):
    """
        Window for adding, editting and copying plans or instructions.


        Adding Item:

        .. image:: ./_static/form_add.png
            :width: 500
            :alt: Add Item Widget
            :align: center

        Editting/Copying Item:

        .. image:: ./_static/form_edit.png
            :width: 400
            :alt: Edit Item Widget
            :align: center

    """

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
        """
            Get the item metadata if it already exists.
        """
        selectedItem = self.model._selected_queue_item_uids
        itemPos = self.model.queue_item_uid_to_pos(selectedItem[0])
        return self.model._plan_queue_items[itemPos]

    def getHasParameters(self, value):
        """
            Detect if a value was inserted.
        """
        hasParam = bool(value) and value != "None"
        if hasParam and isinstance(value, str):
            hasParam = len(value) > 0
        return hasParam

    def handleDetectorValue(self, inputWid, key):
        """
            Transform the detector value to a list if there is only one.
        """
        value = inputWid["widget"].text()
        isDetector = inputWid["kind"] == "POSITIONAL_ONLY" or key == "detectors"
        if isDetector and isinstance(value, str):
            value = [value]
        return value

    def handleNonMotorTypes(self, valueList, widType):
        """
            Create a list for type with only one value.
        """
        if not isinstance(widType, list):
            try:
                len(widType) > 1
            except Exception:
                widType = [widType]
                valueList = [valueList]
        return valueList, widType

    def verifyValueType(self, valueList, widType):
        """
            Verify if the inserted value is valid.
        """
        valueList, widType = self.handleNonMotorTypes(valueList, widType)
        try:
            widTypeLen = len(widType)
            return any([
                typesentry.Config().is_type(value, widType[idx-widTypeLen*floor(idx/widTypeLen)]) for idx, value in enumerate(valueList)
            ])
        except Exception:
            print(valueList, type(valueList), widType)
        return False

    def getItemParameters(self):
        """
            Validate and format the item parameters into dictionary items.
        """
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
        """
            Format item metadata dictionary.
        """
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
        """
            Add or update the queue item.
        """
        itemParameters = self.getItemParameters()
        item = self.getItemMetadata(itemParameters)
        isItemUpdate = "edit" in self.modalMode
        if isItemUpdate:
            self.model.queue_item_update(item=item)
        else:
            self.model.queue_item_add(item=item)
        self.accept()

    def getDialogBtns(self):
        """
            Create the form dialog buttons.
        """
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.btns.accepted.connect(self.addItemToQueue)
        self.btns.rejected.connect(self.reject)

        return self.btns

    def setWidgetValue(self, inputWid, item, isStr):
        """
            Set the widget value if it already has one.
        """
        if isStr:
            inputWid.setText(str(item))
        else:
            inputWid.setValue(item)

    def addDefaultValues(self, paramMeta, inputWid):
        """
            Set the widget default value if it has one.
        """
        placeHolderType = any([isinstance(inputWid, widType) for widType in [QLineEdit, SophysSpinBox]])
        if placeHolderType:
            default = ""
            if "default" in paramMeta:
                default = paramMeta["default"]
            inputWid.setPlaceholderText(default)

    def handleArgsParam(self, argsParams, paramName):
        """
            Format the Args list parameter into the "Detectors" and "Motors" input widgets.
        """
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
        """
        Handle default or existing values when opening the form.
        """
        self.addDefaultValues(paramMeta, inputWid)

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

    def getAvailableDevicesType(self, title):
        """
            Get the key for searching the devices options.
        """
        optionsMode = {
            "motor": "is_movable",
            "detectors": "is_readable",
            "flyers": "is_flyable"
        }
        return optionsMode[title] if title in optionsMode else None

    def getDevicesOptions(self, availableDevices):
        """
            Get all the available devices based on one of its property.
        """
        allowedDevices = self.model._allowed_devices
        optionsList = []
        for key, device in allowedDevices.items():
            if device[availableDevices]:
                optionsList.append(key)
        return optionsList

    def getIterableInput(self, paramMeta, isNumber, isGrouped=False):
        """
            Handle iterable inputs with pre existing options.
        """
        optionsList = None
        availableDevices = self.getAvailableDevicesType(paramMeta["name"])
        if availableDevices:
            optionsList = self.getDevicesOptions(availableDevices)
        return SophysInputList(optionsList, isNumber, not isGrouped)

    def getInputTooltip(self, param):
        """
            Get the parameter description for the input tooltip.
        """
        hasDescription = "description" in param
        if hasDescription:
            description = param["description"]
            try:
                extraIdx = description.index("-.-")
                description = description[:extraIdx]
            except Exception:
                pass
            return description.capitalize()
        return ""

    def getInputWidget(self, paramMeta, paramType):
        """
            Get the parameter widget based on its types.
        """
        isNumber = "int" if "int" in paramType else "float"
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
            inputWid = SophysSpinBox(isNumber)
            inputWid.setMaximumHeight(50)
        else:
            inputWid = QLineEdit()
        self.handleModalMode(inputWid, paramMeta, isStr)
        if not isArgs:
            tooltipMsg = self.getInputTooltip(paramMeta)
            inputWid.setToolTip(tooltipMsg)
        return inputWid

    def getIsRequired(self, paramMeta, varType):
        """
            Get if input is required.
        """
        hasDefaultValue = "default" in paramMeta
        return not (hasDefaultValue or "Optional" in varType)

    def replaceUnknownTypes(self, varType):
        """
            Replace bluesky types for python types in order for the
            type check to work.
        """
        for keyType, replaceType in UNKNOWN_TYPES.items():
            varType = varType.replace(keyType, replaceType)
        return varType

    def convertTypeToPythonType(self, varType):
        varType = self.replaceUnknownTypes(varType)
        return eval(varType) if varType != "" else object

    def getParamPythonType(self, paramMeta):
        """
            Convert a string or an array to a python variable type.
        """
        isArgs = paramMeta["name"] == "args"
        if isArgs:
            motorTyping = getMotorInput(paramMeta)
            motorArray = motorTyping.split(";")
            motorTypes = motorArray[2].split(",")
            arrayType = []
            for strType in motorTypes:
                arrayType.append(self.convertTypeToPythonType(strType))
            return arrayType
        hasAnnotation = "annotation" in paramMeta
        varType = paramMeta["annotation"]["type"] if hasAnnotation else ""
        return self.convertTypeToPythonType(varType)

    def getInputTitle(self, title, isRequired):
        """
            Create the input title widget.
        """
        reqText = " (required)" if isRequired else ""
        lbl = QLabel(title + reqText)
        lbl.setMaximumHeight(50)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def addParameterInput(self, paramMeta, pos, glay):
        """
            Add one parameter input with its title.
        """
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
        """
            Message shown if there are no allowed parameters.
        """
        noParamLbl = "There are no configurable parameters " \
            f"for the choosen {self.itemType}."
        return QLabel(noParamLbl)

    def updateParametersLayout(self, newGroup):
        """
            Update the parameters input layout.
        """
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
        combobox.setEditable(True)
        combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        combobox.setInsertPolicy(QComboBox.NoInsert)
        allowedNames = self.allowedNames()
        combobox.addItems(sorted(allowedNames))
        combobox.activated.connect(
            lambda idx, combobox=combobox: self.changeCurrentItem(combobox.itemText(idx)))
        currItem = combobox.currentText()
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
