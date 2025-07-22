import time
import typing
import qtawesome as qta
import typesentry
from math import floor
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout, \
    QApplication, QCompleter, QComboBox
from sophys_gui.functions import evaluateValue, getMotorInput
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

    def __init__(
            self, model, modalMode, allowedParameters, allowedNames, hasEnv=True, metadata_file_path="",
            form_gui_widget = "", max_rows = 3, max_cols = 3, readingOrder="up_down"):
        super().__init__()
        self.readingOrder = readingOrder
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.form_gui_widget = form_gui_widget
        self.allowedParameters = allowedParameters
        self.allowedNames = allowedNames
        self.inputWidgets = {}
        self.model = model
        self.modalMode = modalMode
        self.hasEnv = hasEnv
        self.plan_description = None
        self.metadata_file_path = None
        self.global_metadata_path = metadata_file_path
        self.itemType = "instruction" if "instruction" in modalMode else "plan"
        self.setupUi()
    
    def accept(self):
        if len(self.form_gui_widget) == 0:
            super().accept()

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
        widget = inputWid["widget"]
        value = widget.currentText() if isinstance(widget, QComboBox) else widget.text()
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
        for idx, types in enumerate(widType):
            generic_type = str(types)
            if "typing.Literal" in generic_type:
                del widType[idx]
                del valueList[idx]
        try:
            widTypeLen = len(widType)
            if widTypeLen == 0:
                return True
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
                if not isinstance(inputWid["widget"], QLineEdit):
                    value = evaluateValue(value)
                if "Literal" in str(inputWid["type"]):
                    value = str(value)
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
            if key == "md" and self.metadata_file_path != None:
                if not hasParam:
                    inputValues["kwargs"]["md"] = {}
                inputValues["kwargs"]["md"]["metadata_save_file_location"] = self.metadata_file_path.text()
                self.global_metadata_path(self.metadata_file_path.text())
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

    def addItemToQueue(self, params=None):
        """
            Add or update the queue item.
        """
        itemParameters = self.getItemParameters()
        item = self.getItemMetadata(itemParameters)
        isItemUpdate = "edit" in self.modalMode
        
        if isItemUpdate:
            self.model.queue_item_update(item=item)
        else:
            self.model.queue_item_add(item=item, params=params)
        self.accept()

    def addStopItem(self):
        allowed_parameters = self.model.get_allowed_instruction_parameters
        allowed_names = self.model.get_allowed_instruction_names
        form = SophysForm(self.model, "add_instruction", allowed_parameters, allowed_names)
        form.addItemToQueue({"pos": "front"})

    def immediateExecution(self):
        """
            Execute only the created plan or instruction in this exact instant.
        """
        if self.chosenItem != "queue_stop":
            self.addStopItem()
        self.addItemToQueue({"pos": "front"})
        self.model.queue_start()

    def getDialogBtns(self, hasAddItemBtn: bool = True):
        """
            Create the form dialog buttons.
        """
        self.btns = QDialogButtonBox()
        if hasAddItemBtn:
            self.btns = QDialogButtonBox(
                QDialogButtonBox.Save | QDialogButtonBox.Cancel
            )
        if "add" in self.modalMode:
            btn = self.btns.addButton("Execute", QDialogButtonBox.ActionRole)
            btn.setIcon(qta.icon("fa5s.play"))
            btn.setEnabled(self.hasEnv)
            btn.clicked.connect(self.immediateExecution)
        self.btns.accepted.connect(self.addItemToQueue)
        self.btns.rejected.connect(self.reject)

        return self.btns

    def setWidgetValue(self, inputWid, item, isStr):
        """
            Set the widget value if it already has one.
        """
        if isinstance(inputWid, QComboBox):
            inputWid.setCurrentText(str(item))
        elif isStr:
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
            if isinstance(inputWid, SophysSpinBox):
                default = 0
            if "default" in paramMeta:
                default = paramMeta["default"]
            inputWid.setPlaceholderText(default)
        elif isinstance(inputWid, QComboBox):
            if "default" in paramMeta:
                inputWid.setCurrentText(paramMeta["default"])

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
            if hasArgs and (item == None):
                item = self.handleArgsParam(metadata["args"], paramName)
            if (item != None):
                self.setWidgetValue(inputWid, item, isStr)

    def getAvailableDevicesType(self, title):
        """
            Get the key for searching the devices options.
        """
        optionsMode = {
            "__MOVABLE__": "is_movable",
            "__READABLE__": "is_readable",
            "__FLYABLE__": "is_flyable"
        }
        for device_type, http_server_key in optionsMode.items():
            if device_type in title:
                return http_server_key
        return None

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

    def getIterableInput(self, paramMeta, inputType, isGrouped=False):
        """
            Handle iterable inputs with pre existing options.
        """
        optionsList = None
        if "motor" in paramMeta["name"]:
            inputType = "__MOVABLE__"
        if inputType:
            availableDevices = self.getAvailableDevicesType(inputType)
            if availableDevices:
                optionsList = self.getDevicesOptions(availableDevices)
            else:
                inputType = "int" if "int" in inputType else "float" if "float" in inputType else None
        return SophysInputList(optionsList, inputType, not isGrouped)

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
            return description
        return ""

    def getComboboxInput(self, inputType, insertAvailable):
        combobox = QComboBox()
        combobox.setEditable(True)
        combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        insert_mode = QComboBox.InsertAlphabetically if insertAvailable else QComboBox.NoInsert
        combobox.setInsertPolicy(insert_mode)

        availableDevices = self.getAvailableDevicesType(inputType)
        if "bool" in inputType:
            combobox.addItems(["True", "False"])
        elif "Literal" in inputType:
            literal_idx = inputType.index("Literal")
            splitStr = inputType[literal_idx+8:].replace(" '", "").replace("'", "")
            options_end_idx = splitStr.index("]")
            combobox.addItems(splitStr[:options_end_idx].split(","))
        elif availableDevices:
            optionsList = self.getDevicesOptions(availableDevices)
            combobox.addItems(sorted(optionsList))
        return combobox

    def getInputWidget(self, paramMeta, paramType, isRequired):
        """
            Get the parameter widget based on its types.
        """
        strType = str(paramType)
        isDevice = any([item in strType for item in ["__MOVABLE__", "__READABLE__", "__FLYABLE__"]])
        isNumber = any([item in strType for item in ["int", "float"]])
        isIterable = any([item in strType for item in ["Sequence", "Iterable", "list", "object"]])
        isBool = "bool" in strType
        isLiteral = "Literal" in strType
        isArgs = "-.-" in paramMeta["description"] if "description" in paramMeta else False
        isDict  = "dict" in strType
        isStr = "str" in strType
        if isDict:
            inputWid = SophysInputDict()
        elif isArgs:
            inputWid = SophysInputMotor(paramMeta, self.getIterableInput)
        elif isIterable and not isBool:
            inputWid = self.getIterableInput(paramMeta, paramType)
        elif isDevice or isLiteral or isBool:
            inputWid = self.getComboboxInput(paramType, isStr)
        elif isNumber:
            numericType = "int" if "int" in paramType else "float"
            inputWid = SophysSpinBox(numericType, isRequired)
            inputWid.setMaximumHeight(50)
        else:
            isStr = True
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
        isArgs = "-.-" in paramMeta["description"] if "description" in paramMeta else False
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
        return varType

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
        isRequired = self.getIsRequired(paramMeta, paramType)

        title = paramMeta["name"]
        lbl = self.getInputTitle(title, isRequired)
        glay.addWidget(lbl, *pos, 1, 1)
        pos[0] += 1

        rowStretch = 1 if title != "md" else 6 - pos[0]
        inputWid = self.getInputWidget(paramMeta, paramType, isRequired)
        glay.addWidget(inputWid, *pos, rowStretch, 1)
        pos[0] += 1
        
        pythonType = self.getParamPythonType(paramMeta)
        if isinstance(pythonType, str):
            pythonType = self.convertTypeToPythonType(pythonType)
        self.inputWidgets[title] = {
            "widget": inputWid,
            "required": isRequired,
            "type": pythonType,
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
        itemAllowedParams = None
        retry_count = 0
        while itemAllowedParams == None and retry_count <= 5:
            itemAllowedParams = self.allowedParameters(name=currentItem)
            time.sleep(0.2)
            retry_count += 1
        if retry_count > 5 and itemAllowedParams is None:
            raise Exception()

        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)

        if "description" in itemAllowedParams and self.plan_description != None:
            self.plan_description.setText(itemAllowedParams["description"])

        self.chosenItem = itemAllowedParams["name"]
        group.setTitle(self.chosenItem)

        hasParameters = "parameters" in itemAllowedParams
        if hasParameters:
            parameters = itemAllowedParams["parameters"]
            self.inputWidgets = {}
            pos = [0, 0]
            for paramMeta in parameters:
                pos = self.addParameterInput(paramMeta, pos, glay)
                if self.readingOrder == "up_down":
                    if pos[0] >= self.max_rows*2:
                        pos[0] = 0
                        pos[1] += 2
                else:
                    if pos[1] >= self.max_cols - 1:
                        pos[1] = 0
                        pos[0] += 1
                    else:
                        pos[1] += 1
                        pos[0] -= 2
        else:
            glay.addWidget(self.getNoParametersLabel())
        self.updateParametersLayout(group)

    def getGeneralPlanData(self):
        """
            Create combobox for choosing the plan or instruction to add.
            Only appear when creating a new plan or instruction.
        """
        group = QGroupBox()
        group.setMaximumHeight(150)
        vlay = QVBoxLayout()
        group.setLayout(vlay)
        group.setTitle(self.itemType)

        combobox = QComboBox()
        combobox.setEditable(True)
        combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        combobox.setInsertPolicy(QComboBox.NoInsert)
        allowedNames = self.allowedNames()
        combobox.addItems(sorted(allowedNames))
        combobox.activated.connect(
            lambda idx, combobox=combobox: self.changeCurrentItem(combobox.itemText(idx)))
        currItem = combobox.currentText()
        vlay.addWidget(combobox)

        self.plan_description = QLabel()
        vlay.addWidget(self.plan_description)

        if self.itemType == "plan" and self.global_metadata_path != "":
            hbox = QHBoxLayout()
            metadata_lbl = QLabel("Metadata File Path")
            hbox.addWidget(metadata_lbl)
            self.metadata_file_path = QLineEdit(self.global_metadata_path())
            hbox.addWidget(self.metadata_file_path)
            vlay.addLayout(hbox)

        return group, currItem

    def setupUi(self):
        self.setMaximumSize(1500, 1000)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.group = QGroupBox()
        self.parametersLayout = QGridLayout()
        lay = QVBoxLayout(self)

        isAddition = "add" in self.modalMode
        if len(self.form_gui_widget) > 0:
            currItem = self.form_gui_widget
        else:
            if isAddition:
                itemCombbox, currItem = self.getGeneralPlanData()
                lay.addWidget(itemCombbox)
            else:
                currItem = self.selectedItemMetadata()["name"]

        self.changeCurrentItem(currItem)
        lay.addLayout(self.parametersLayout)

        btns = self.getDialogBtns(len(self.form_gui_widget) == 0)
        lay.addWidget(btns)

        app = QApplication.instance()
        app.createPopup(self)
