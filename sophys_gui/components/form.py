import typing
import ast
import typesentry
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout, \
    QApplication
from .input import SophysInputList, SophysInputDict, SophysSpinBox


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

    def selectedItemMetadata(self):
        sel_item = self.model._selected_queue_item_uids
        pos = self.model.queue_item_uid_to_pos(sel_item[0])
        return self.model._plan_queue_items[pos]

    def getPlanParameters(self):
        inputValues = {}
        isValid = True

        if self.item_type == 'instruction':
            return isValid

        for key, inputWid in self.inputWidgets.items():
            value = inputWid["widget"].text()
            hasParam = True
            try:
                hasParam = len(value) > 0
            except Exception:
                print("")
            if hasParam:
                try:
                    value = ast.literal_eval(value)
                except Exception:
                    value = value
                try:
                    validParam = typesentry.Config().is_type(value, inputWid['type'])
                except Exception:
                    print(value, inputWid['type'])
                if validParam:
                    inputValues[key] = value
                else:
                    inputWid["widget"].setStyleSheet("border: 1px solid #ff0000;")
                    isValid = False
                    exception = "001: Invalid Input type!!"
            elif inputWid["required"]:
                inputWid["widget"].setStyleSheet("border: 1px solid #ff0000;")
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
        if self.item_type == 'plan':
            metadata['args'] = []
            metadata['kwargs'] = plan_parameters
        if self.modalMode == 'edit':
            metadata['item_uid'] = self.selectedItemMetadata()['item_uid']
        return metadata

    def addPlanToQueue(self):
        plan_parameters = self.getPlanParameters()
        item = self.getPlanMetadata(plan_parameters)
        if self.modalMode == "edit":
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

    def handleModalMode(self, inputWid, paramMeta, isStr):
        if self.modalMode != "add":
            paramName = paramMeta["name"]
            itemParams = self.selectedItemMetadata()['kwargs']
            if paramName in itemParams:
                item = itemParams[paramName]
                if isStr:
                    inputWid.setText(str(item))
                else:
                    inputWid.setValue(item)
                return
        if isinstance(inputWid, QLineEdit) or isinstance(inputWid, SophysSpinBox):
            default = ''
            if "default" in paramMeta:
                default = paramMeta["default"]
            inputWid.setPlaceholderText(default)

    def getInputWidget(self, paramMeta, paramType):
        isNumber =any([True if numType in paramType else False for numType in ['int', 'float']])
        isIterable = 'Iterable' in paramType
        isDict  = 'dict' in paramType
        if isDict:
            inputWid = SophysInputDict()
        elif isIterable:
            inputWid = SophysInputList(None, isNumber, isNumber)
        elif isNumber:
            inputWid = SophysSpinBox()
        else:
            inputWid = QLineEdit()

        # inputWid.textChanged.connect(
        #     lambda _, wid=inputWid: wid.setStyleSheet("border: 1px solid #777;"))
        isStr = not (isNumber or isDict or isIterable)
        self.handleModalMode(inputWid, paramMeta, isStr)

        return inputWid

    def isRequired(self, paramMeta):
        hasDefaultValue = "default" in paramMeta
        return not (hasDefaultValue)

    def addParameterInput(self, paramMeta, pos, glay):
        isRequired = self.isRequired(paramMeta)
        NoneType = type(None)
        paramType = eval(paramMeta['annotation']['type']) if 'annotation' in paramMeta else object

        title = paramMeta["name"]
        reqText = ' (required)' if isRequired else ''
        lbl = QLabel(title + reqText)
        lbl.setAlignment(Qt.AlignCenter)
        glay.addWidget(lbl, *pos)
        pos[0] += 1

        inputWid = self.getInputWidget(paramMeta, str(paramType))
        glay.addWidget(inputWid, *pos)
        pos[0] += 1

        self.inputWidgets[title] = {
            "widget": inputWid,
            "required": isRequired,
            "type": paramType
        }

        return pos

    def changePlan(self, currentPlan):
        allowed_params = self.allowed_parameters(name=currentPlan)

        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)
        self.setChosenItem(allowed_params["name"])
        group.setTitle(self.chosenItem)
        parameters = allowed_params["parameters"]
        self.inputWidgets = {}

        pos = [0, 0]
        for paramMeta in parameters:
            pos = self.addParameterInput(paramMeta, pos, glay)
            if pos[0] > 4:
                pos[0] = 0
                pos[1] += 2

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
        if 'instruction' != self.item_type:
            cb.activated.connect(lambda idx, cb=cb: self.changePlan(cb.itemText(idx)))
            self.changePlan(cb.itemText(0))
        else:
            cb.activated.connect(lambda idx, cb=cb: self.setChosenItem(cb.itemText(idx)))
            self.setChosenItem(cb.itemText(0))
        hlay.addWidget(cb)

        return group

    def setupUi(self):
        lay = QVBoxLayout(self)

        if 'add' in self.modalMode:
            planCb = self.changeCurrentPlan()
            lay.addWidget(planCb)
        else:
            self.changePlan(self.selectedItemMetadata()['name'])

        if 'instruction' != self.item_type:
            lay.addLayout(self.planParameters)

        btns = self.getDialogBtns()
        lay.addWidget(btns)

        app = QApplication.instance()
        app.createPopup(self)
