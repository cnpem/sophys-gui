import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QGridLayout, QLineEdit, QVBoxLayout, QStackedWidget, \
    QSizePolicy


class SophysInputDict(QWidget):

    def __init__(self):
        super().__init__()
        self.inputDict = {}
        self.inputWid = []
        self.rowIndex = 0
        self.valueEdit = {}
        self._setupUi()

    def text(self):
        """
            Return dictionary value.
        """
        return self.inputDict

    def setValue(self, item):
        """
            Set pre-existing dictionary value.
        """
        self.inputDict = item
        self.createAllInputDict()

    def saveEditRow(self, key, row):
        """
            Save a new value for a dictionary item.
        """
        newValue = self.valueEdit[key].text()
        self.inputDict[key] = newValue
        self.toggleEditRow(row, 0)
        self.inputWid[row][1].currentWidget().setText(newValue)
        self.inputWid[row][1].currentWidget().setText(newValue)

    def toggleEditRow(self, row, value):
        for col in range(1, 3):
            self.inputWid[row][col].setCurrentIndex(value)

    def createAllInputDict(self):
        """
            Create the list with all the existing keys and values of
            the dictionary.
        """
        self.rowIndex = 0
        self.inputWid = []
        for key, value in self.inputDict.items():
            self.createKeyValueWidget(key, value)

    def deleteRow(self, key):
        """
            Delete a dictionary item and its row on the GUI.
        """
        del self.inputDict[key]
        for widgetList in self.inputWid:
            for widget in widgetList:
                widget.deleteLater()
        self.createAllInputDict()

    def createValueStack(self, key, value):
        """
            Create a stack for editing or showing a value of a dictionary item.
        """
        valueStack = QStackedWidget()
        valueStack.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        valueLbl = QLabel(value)
        valueLbl.setAlignment(Qt.AlignCenter)
        valueStack.addWidget(valueLbl)

        self.valueEdit[key] = QLineEdit(value)
        valueStack.addWidget(self.valueEdit[key])

        return valueStack

    def editSaveStack(self, key):
        """
            Create a stack for enabling editing the value of a dictionary
            item and saving its new value.
        """
        editStack = QStackedWidget()
        editStack.setFixedSize(40, 25)

        editBtn = QPushButton("")
        editBtn.setIcon(qta.icon("fa5s.pencil-alt"))
        editBtn.clicked.connect(lambda _, row=self.rowIndex: self.toggleEditRow(row, 1))
        editStack.addWidget(editBtn)

        saveBtn = QPushButton("")
        saveBtn.setIcon(qta.icon("fa5.save"))
        saveBtn.clicked.connect(lambda _, key=key, row=self.rowIndex: self.saveEditRow(key, row))
        editStack.addWidget(saveBtn)

        return editStack

    def createKeyValueWidget(self, key, value):
        keyLbl = QLabel(key)
        keyLbl.setAlignment(Qt.AlignCenter)
        keyLbl.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.inputDictList.addWidget(keyLbl, self.rowIndex, 0)

        valueStack = self.createValueStack(key, value)
        self.inputDictList.addWidget(valueStack, self.rowIndex, 1)

        editStack = self.editSaveStack(key)
        self.inputDictList.addWidget(editStack, self.rowIndex, 2)

        deleteBtn = QPushButton("")
        deleteBtn.setFixedSize(40, 25)
        deleteBtn.setIcon(qta.icon("fa5s.trash-alt"))
        deleteBtn.clicked.connect(lambda _, key=key: self.deleteRow(key))
        self.inputDictList.addWidget(deleteBtn, self.rowIndex, 3)

        self.inputWid.append([
            keyLbl, valueStack, editStack, deleteBtn
        ])
        self.rowIndex += 1

    def addDictionaryItem(self):
        """
            Add a new dictionary key/value pair and add it to the widget list.
        """
        key = self.keyInput.text()
        value = self.valueInput.text()

        isValidInput = key and value and not key in self.inputDict
        if isValidInput:
            self.inputDict[key] = value
            self.createKeyValueWidget(key, value)

    def getKeyValueInput(self):
        """
            Create a widget for inserting a key and a value.
        """
        glay = QGridLayout()
        glay.setAlignment(Qt.AlignTop)

        for idy, title in enumerate(["Key", "Value"]):
            lbl = QLabel(title)
            lbl.setAlignment(Qt.AlignCenter)
            glay.addWidget(lbl, 0, idy)

            edit = QLineEdit()
            edit.setMinimumWidth(100)
            glay.addWidget(edit, 1, idy)

            isValue = title == "Value"
            if isValue:
                self.valueInput = edit
            else:
                self.keyInput = edit

        addBtn = QPushButton()
        addBtn.setIcon(qta.icon("fa5s.plus"))
        addBtn.setFixedSize(40, 25)
        addBtn.clicked.connect(self.addDictionaryItem)
        glay.addWidget(addBtn, 1, 2, 1, 1)

        return glay

    def _setupUi(self):
        vlay = QVBoxLayout()
        vlay.setContentsMargins(2, 2, 2, 2)
        vlay.setSpacing(2)

        keyValueWid = self.getKeyValueInput()
        vlay.addLayout(keyValueWid, 1)

        self.inputDictList = QGridLayout()
        vlay.addLayout(self.inputDictList, 4)

        self.setLayout(vlay)
