from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout
from .popup import PopupWidget


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
            if len(value) > 0:
                inputValues[key] = value
            elif inputWid["required"]:
                inputWid["widget"].setStyleSheet("border: 1px solid #ff0000;")
                isValid = False

        if not isValid:
            return False
        return inputValues

    def getPlanMetadata(self, plan_parameters):
        metadata = {
            'item_type': self.item_type,
            'name': self.chosenItem
        }
        if self.item_type == 'plan':
            metadata['args'] = []
            metadata['kwargs'] = plan_parameters
        if self.modalMode == 'edit':
            metadata['item_uid'] = self.selectedItemMetadata()['item_uid']
        return metadata

    def addPlanToQueue(self):
        plan_parameters = self.getPlanParameters()
        if plan_parameters:
            item = self.getPlanMetadata(plan_parameters)
            try:
                if self.modalMode == "edit":
                    self.model.queue_item_update(item=item)
                else:
                    self.model.queue_item_add(item=item)
                self.accept()
            except Exception:
                self.popup.set_text("Parameter input error!!")
                self.popup.show_popup()
        else:
            self.popup.set_text("Missing required fields!!")
            self.popup.show_popup()

    def getDialogBtns(self):
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.btns.accepted.connect(self.addPlanToQueue)
        self.btns.rejected.connect(self.reject)

        return self.btns

    def handleModalMode(self, inputWid, paramMeta):
        if self.modalMode != "add":
            paramName = paramMeta["name"]
            itemParams = self.selectedItemMetadata()['kwargs']
            if paramName in itemParams:
                inputWid.setText(str(itemParams[paramName]))
                return
        default = ''
        if "default" in paramMeta:
            default = paramMeta["default"]
        inputWid.setPlaceholderText(default)

    def getInputWidget(self, paramMeta):
        inputWid = QLineEdit()
        inputWid.textChanged.connect(
            lambda _, wid=inputWid: wid.setStyleSheet("border: 1px solid #777;"))
        self.handleModalMode(inputWid, paramMeta)

        return inputWid

    def isRequired(self, paramMeta):
        kindName = paramMeta["kind"]["name"]
        isKeyword = 'KEYWORD_ONLY' == kindName
        isPositional = 'POSITIONAL_ONLY' == kindName
        hasDefaultValue = "default" in paramMeta
        return not (hasDefaultValue or isPositional or isKeyword)

    def addParameterInput(self, paramMeta, pos, glay):
        isRequired = self.isRequired(paramMeta)

        title = paramMeta["name"]
        reqText = ' (required)' if isRequired else ''
        lbl = QLabel(title + reqText)
        lbl.setAlignment(Qt.AlignCenter)
        glay.addWidget(lbl, *pos)
        pos[0] += 1

        inputWid = self.getInputWidget(paramMeta)
        glay.addWidget(inputWid, *pos)
        pos[0] += 1

        self.inputWidgets[title] = {
            "widget": inputWid,
            "required": isRequired
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
        cb.addItems(self.allowed_names())
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

        self.popup = PopupWidget(self)
        self.popup.setVisible(False)
