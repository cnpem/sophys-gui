import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, \
    QPushButton, QGridLayout, QGroupBox, QHBoxLayout, \
    QLineEdit, QVBoxLayout, QHBoxLayout, QStackedWidget, \
    QSizePolicy, QCheckBox, QSpinBox


class SophysInputList(QWidget):

    def __init__(self, itemList, isNumber, optionalList=False):
        super().__init__()
        self.selectedItems = []
        self.selectedWidgets = []
        self.availableItems = itemList
        self.isNumber = isNumber
        self.optionalList = optionalList
        self.curr_index = [0, 0]
        self._setupUi()

    def text(self):
        if self.optionalList and len(self.selectedItems)==1:
            return self.selectedItems[0]
        return self.selectedItems

    def setValue(self, value):
        if not isinstance(value, list):
            value = [value]
        self.selectedItems = value
        self.showSelectedItems(self.selectedItems)

    def getSelectedTag(self, title):
        group = QGroupBox()
        hlay = QHBoxLayout()
        hlay.setContentsMargins(2, 2, 2, 2)
        group.setLayout(hlay)

        itemLbl = QLabel(str(title))
        itemLbl.setAlignment(Qt.AlignCenter)
        hlay.addWidget(itemLbl)

        removeItem = QPushButton()
        removeItem.setIcon(qta.icon("fa.close"))
        removeItem.clicked.connect(
            lambda _, item=title: self.removeItem(item))
        hlay.addWidget(removeItem)

        return group

    def showSelectedItems(self, selItems):
        for item in selItems:
            tag = self.getSelectedTag(item)
            self.selectedWidgets.append(tag)
            self.selectedItemList.addWidget(tag, *self.curr_index)
            self.curr_index[1] += 1
            if self.curr_index[1] > 2:
                self.curr_index[1] = 0
                self.curr_index[0] += 1

    def removeItem(self, item):
        for wid in self.selectedWidgets:
            wid.deleteLater()
        self.selectedWidgets = []
        self.curr_index = [0, 0]
        self.selectedItems.remove(item)
        self.showSelectedItems(self.selectedItems)

        if self.availableItems != None:
            self.availableItems.append(item)
            self.edit.clear()
            self.edit.addItems(self.availableItems)

    def selectItem(self):
        if self.availableItems != None:
            selectedItem = self.edit.currentText()
            if selectedItem and not selectedItem in self.selectedItems:
                self.selectedItems.append(selectedItem)
                self.showSelectedItems([selectedItem])

                self.availableItems.remove(selectedItem)
                self.edit.clear()
                self.edit.addItems(self.availableItems)
            return
        elif self.isNumber:
            value = self.edit.value()
        else:
            value = self.edit.text()
        self.selectedItems.append(value)
        self.showSelectedItems([value])

    def _setupUi(self):
        glay = QGridLayout()
        glay.setContentsMargins(2, 2, 2, 2)
        glay.setSpacing(2)

        if self.availableItems != None:
            wid = QComboBox()
            wid.addItems(self.availableItems)
        elif self.isNumber:
            wid = QSpinBox()
        else:
            wid = QLineEdit()
        glay.addWidget(wid, 0, 0, 1, 2)
        self.edit = wid

        addBtn = QPushButton()
        addBtn.setIcon(qta.icon("fa5s.plus"))
        addBtn.clicked.connect(self.selectItem)
        glay.addWidget(addBtn, 0, 2, 1, 1)

        self.selectedItemList = QGridLayout()
        self.selectedItemList.setContentsMargins(0, 0, 0, 0)
        self.selectedItemList.setSpacing(2)
        glay.addLayout(self.selectedItemList, 1, 0, 2, 3)

        self.setLayout(glay)


class SophysInputDict(QWidget):

    def __init__(self):
        super().__init__()
        self.inputDict = {}
        self.inputWid = []
        self.rowIndex = 0
        self.valueEdit = {}
        self._setupUi()

    def text(self):
        return self.inputDict

    def setValue(self, item):
        self.inputDict = item
        self.createAllInputDict()

    def saveEditRow(self, key, row):
        newValue = self.valueEdit[key].text()
        self.inputDict[key] = newValue
        self.inputWid[row][1].currentWidget().setText(newValue)
        self.inputWid[row][1].setCurrentIndex(0)
        self.inputWid[row][1].currentWidget().setText(newValue)
        self.inputWid[row][2].setCurrentIndex(0)

    def editRow(self, row):
        self.inputWid[row][1].setCurrentIndex(1)
        self.inputWid[row][2].setCurrentIndex(1)

    def createAllInputDict(self):
        self.rowIndex = 0
        self.inputWid = []
        for key, value in self.inputDict.items():
            self.createKeyValueWidget(key, value)

    def deleteRow(self, key):
        del self.inputDict[key]
        for widgetList in self.inputWid:
            for widget in widgetList:
                widget.deleteLater()
        self.createAllInputDict()

    def createValueStack(self, key, value):
        valueStack = QStackedWidget()

        valueLbl = QLabel(value)
        valueLbl.setAlignment(Qt.AlignCenter)
        valueStack.addWidget(valueLbl)

        self.valueEdit[key] = QLineEdit(value)
        valueStack.addWidget(self.valueEdit[key])

        return valueStack

    def createKeyValueWidget(self, key, value):
        keyLbl = QLabel(key)
        keyLbl.setAlignment(Qt.AlignCenter)
        keyLbl.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.inputDictList.addWidget(keyLbl, self.rowIndex, 0)

        valueStack = self.createValueStack(key, value)
        valueStack.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.inputDictList.addWidget(valueStack, self.rowIndex, 1)

        editStack = QStackedWidget()
        editStack.setFixedSize(40, 25)
        editBtn = QPushButton("")
        editBtn.setIcon(qta.icon("fa5s.pencil-alt"))
        editBtn.clicked.connect(lambda _, row=self.rowIndex: self.editRow(row))
        editStack.addWidget(editBtn)

        editBtn = QPushButton("")
        editBtn.setIcon(qta.icon("fa5.save"))
        editBtn.clicked.connect(lambda _, key=key, row=self.rowIndex: self.saveEditRow(key, row))
        editStack.addWidget(editBtn)

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
        key = self.keyInput.text()
        value = self.valueInput.text()

        if key and value and not key in self.inputDict:
            self.inputDict[key] = value
            self.createKeyValueWidget(key, value)

    def getKeyValueInput(self):
        glay = QGridLayout()

        lbl = QLabel("Key")
        lbl.setAlignment(Qt.AlignCenter)
        glay.addWidget(lbl, 0, 0)

        self.keyInput = QLineEdit()
        glay.addWidget(self.keyInput, 1, 0)

        lbl = QLabel("Value")
        lbl.setAlignment(Qt.AlignCenter)
        glay.addWidget(lbl, 0, 1)

        self.valueInput = QLineEdit()
        glay.addWidget(self.valueInput, 1, 1)

        addBtn = QPushButton()
        addBtn.setIcon(qta.icon("fa5s.plus"))
        addBtn.setFixedSize(82, 25)
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


class SophysSpinBox(QWidget):

    def __init__(self):
        super().__init__()
        self.value = None
        self._setupUi()

    def text(self):
        return str(self.value)

    def setPlaceholderText(self, value):
        if value == '' or value == 'None':
            self.stack.setCurrentIndex(0)
        else:
            self.spinbox.setValue(float(value))
            self.stack.setCurrentIndex(1)
            self.cb.setChecked(True)
        self.value = value

    def setValue(self, value):
        self.value = value
        self.spinbox.setValue(value)
        self.stack.setCurrentIndex(1)
        self.cb.setChecked(True)

    def toggleStack(self, value):
        self.stack.setCurrentIndex(value)
        if not value:
            self.value = ''

    def _setupUi(self):
        hlay = QHBoxLayout(self)

        self.cb = QCheckBox()
        hlay.addWidget(self.cb)

        self.stack = QStackedWidget()
        hlay.addWidget(self.stack)

        noneLbl = QLabel("None")
        self.stack.addWidget(noneLbl)

        self.spinbox = QSpinBox()
        self.spinbox.valueChanged.connect(self.setValue)
        self.stack.addWidget(self.spinbox)

        self.cb.clicked.connect(self.toggleStack)
