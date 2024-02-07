from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, \
    QComboBox, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QVBoxLayout


class SophysForm(QDialog):

    def __init__(self, model):
        super().__init__()
        self.inputWidgets = {}
        self.model = model
        self.group = QGroupBox()
        self.planParameters = QGridLayout()
        self.setMaximumSize(1000, 500)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setupUi()

    def getPlanParameters(self):
        inputValues = {}
        isValid = True
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
        return {
            'item_type': 'plan',
            'name': 'count',
            'args': [],
            'kwargs': plan_parameters
        }

    def addPlanToQueue(self):
        plan_parameters = self.getPlanParameters()
        if plan_parameters:
            item = self.getPlanMetadata(plan_parameters)
            self.model.queue_item_add(item=item)
            self.accept()

    def getDialogBtns(self):
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        self.btns.accepted.connect(self.addPlanToQueue)
        self.btns.rejected.connect(self.reject)

        return self.btns

    def getInputWidget(self, paramMeta):
        default = ''
        if "default" in paramMeta:
            default = paramMeta["default"]

        inputWid = QLineEdit()
        inputWid.textChanged.connect(
            lambda _, wid=inputWid: wid.setStyleSheet("border: 1px solid #777;"))
        inputWid.setPlaceholderText(default)

        return inputWid

    def isRequired(self, paramMeta):
        kindName = paramMeta["kind"]["name"]
        isKeyword = 'KEYWORD_ONLY' == kindName
        isPositional = 'POSITIONAL_ONLY' == kindName
        hasDefaultValue = "default" in paramMeta
        return not (hasDefaultValue or isPositional or isKeyword)

    def changePlan(self, currentPlan):
        allowed_params = self.model.get_allowed_plan_parameters(name=currentPlan)
        group = QGroupBox()
        glay = QGridLayout()
        group.setLayout(glay)
        group.setTitle(allowed_params["name"])
        parameters = allowed_params["parameters"]
        self.inputWidgets = {}

        pos = [0, 0]
        for paramMeta in parameters:
            isRequired = self.isRequired(paramMeta)

            title = paramMeta["name"]
            reqText = ' (required)' if isRequired else ''
            lbl = QLabel(title + reqText)
            lbl.setAlignment(Qt.AlignCenter)
            glay.addWidget(lbl, *pos)
            pos[0] += 1

            inputWid = self.getInputWidget(paramMeta)
            glay.addWidget(inputWid, *pos)

            self.inputWidgets[title] = {
                "widget": inputWid,
                "required": isRequired
            }

            pos[0] += 1
            if pos[0] > 4:
                pos[0] = 0
                pos[1] += 2

        self.group.deleteLater()
        self.planParameters.addWidget(group)
        self.group = group

    def changeCurrentPlan(self):
        group = QGroupBox()
        group.setMaximumHeight(75)
        hlay = QHBoxLayout()
        group.setLayout(hlay)
        group.setTitle("Plan")

        cb = QComboBox()
        cb.addItems(self.model.get_allowed_plan_names())
        cb.activated.connect(lambda idx, cb=cb: self.changePlan(cb.itemText(idx)))
        self.changePlan(cb.itemText(0))
        hlay.addWidget(cb)

        return group

    def setupUi(self):
        lay = QVBoxLayout()

        planCb = self.changeCurrentPlan()
        lay.addWidget(planCb)

        lay.addLayout(self.planParameters)

        btns = self.getDialogBtns()
        lay.addWidget(btns)

        self.setLayout(lay)
