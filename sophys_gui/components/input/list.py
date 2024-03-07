import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, \
    QPushButton, QGridLayout, QGroupBox, QHBoxLayout, \
    QLineEdit, QHBoxLayout, QDoubleSpinBox, QSpinBox, QCompleter
from sophys_gui.functions import evaluateValue


class SophysInputList(QWidget):

    def __init__(self, itemList, isNumber, hasAddBtn=True):
        super().__init__()
        self.selectedItems = []
        self.selectedWidgets = []
        self.availableItems = itemList
        self.isNumber = isNumber
        self.hasAddBtn = hasAddBtn
        self.removeFunction = []
        self.curr_index = [0, 0]
        self._setupUi()

    def evaluateList(self, itemList):
            newItem = []
            for value in itemList:
                newValue = self.evaluateNumber(value)
                newItem.append(newValue)
            return newItem

    def evaluateNumber(self, item):
        item = evaluateValue(item)
        if isinstance(item, list):
            item = self.evaluateList(item)
        if isinstance(item, str):
            if (item.strip('-')).isnumeric():
                item = evaluateValue(item)
        return item

    def text(self):
        if len(self.selectedItems)==1:
            return self.evaluateNumber(self.selectedItems[0])
        evaluatedItems = self.evaluateList(self.selectedItems)
        return evaluatedItems

    def setValue(self, value):
        if not isinstance(value, list):
            value = [value]
        self.selectedItems = value
        self.showSelectedItems(self.selectedItems)
        if self.availableItems != None:
            for val in value:
                self.availableItems.remove(val)
            self.edit.clear()
            self.edit.addItems(sorted(self.availableItems))

    def getSelectedTag(self, title):
        group = QGroupBox()
        hlay = QHBoxLayout()
        hlay.setContentsMargins(2, 2, 2, 2)
        group.setLayout(hlay)

        itemLbl = QLabel(str(title))
        itemLbl.setAlignment(Qt.AlignCenter)
        hlay.addWidget(itemLbl)

        if self.hasAddBtn:
            removeItem = QPushButton()
            removeItem.setIcon(qta.icon("fa.close"))
            removeItem.setFixedSize(40, 25)
            removeItem.clicked.connect(
                lambda _, item=title: self.removeItem(item))
            hlay.addWidget(removeItem)
        else:
            self.removeFunction.append(lambda _, item=title: self.removeItem(item))

        return group

    def showSelectedItems(self, selItems):
        colLenght = 2 if self.hasAddBtn else 0
        for item in selItems:
            tag = self.getSelectedTag(item)
            self.selectedWidgets.append(tag)
            self.selectedItemList.addWidget(tag, *self.curr_index)
            self.curr_index[1] += 1
            if self.curr_index[1] > colLenght:
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
            self.edit.addItems(sorted(self.availableItems))

    def selectItem(self):
        if self.availableItems != None:
            selectedItem = self.edit.currentText()
            if selectedItem and not selectedItem in self.selectedItems:
                self.selectedItems.append(selectedItem)
                self.showSelectedItems([selectedItem])

                self.availableItems.remove(selectedItem)
                self.edit.clear()
                self.edit.addItems(sorted(self.availableItems))
                return True
            return False
        elif self.isNumber:
            value = self.edit.value()
        else:
            value = self.edit.text()
            if len(value)==0:
                return False
        self.selectedItems.append(value)
        self.showSelectedItems([value])
        return True

    def setTooltip(self, args):
        return super().setToolTip(args)

    def _setupUi(self):
        glay = QGridLayout()
        minWid = 50
        if self.availableItems != None:
            wid = QComboBox()
            minWid = 100
            wid.setEditable(True)
            wid.completer().setCompletionMode(QCompleter.PopupCompletion)
            wid.setInsertPolicy(QComboBox.NoInsert)
            wid.addItems(sorted(self.availableItems))
        elif self.isNumber:
            if "int" in self.isNumber:
                wid = QSpinBox()
                wid.setMaximum(10000)
            elif "float" in self.isNumber:
                wid = QDoubleSpinBox()
                wid.setMaximum(10000)
        else:
            wid = QLineEdit()
        wid.setMinimumWidth(minWid)
        glay.addWidget(wid, 0, 0, 1, 2)
        self.edit = wid

        if self.hasAddBtn:
            addBtn = QPushButton()
            addBtn.setFixedSize(40, 25)
            addBtn.setIcon(qta.icon("fa5s.plus"))
            addBtn.clicked.connect(self.selectItem)
            glay.addWidget(addBtn, 0, 2, 1, 1)

        self.selectedItemList = QGridLayout()
        self.selectedItemList.setContentsMargins(0, 0, 0, 0)
        self.selectedItemList.setSpacing(2)
        stretch = 3 if self.hasAddBtn else 2
        glay.addLayout(self.selectedItemList, 1, 0, 2, stretch)

        self.setLayout(glay)
