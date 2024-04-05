import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, \
    QPushButton, QGridLayout, QGroupBox, QHBoxLayout, \
    QLineEdit, QHBoxLayout, QCompleter
from sophys_gui.functions import evaluateValue, handleSpinboxWidget


class SophysInputList(QWidget):
    """
        Widget for inserting item in a list format.

        Float List:

        .. image:: ./_static/float_list.png
            :width: 500
            :alt: Float List Input Widget
            :align: center

        Combobox List:

        .. image:: ./_static/cb_list.png
            :width: 400
            :alt: Combobox List Input Widget
            :align: center

        List with items:

        .. image:: ./_static/item_list.png
            :width: 400
            :alt: Float List Input Widget with items
            :align: center
    """

    def __init__(self, itemList, isNumber, isSingle=True):
        super().__init__()
        self.selectedItems = []
        self.selectedWidgets = []
        self.availableItems = itemList
        self.isNumber = isNumber
        self.isSingle = isSingle
        self.removeFunction = []
        self.curr_index = [0, 0]
        self._setupUi()

    def evaluateList(self, itemList):
        """
            Evaluate lists items types.
        """
        newItem = []
        for value in itemList:
            newValue = self.evaluatePythonType(value)
            newItem.append(newValue)
        return newItem

    def evaluatePythonType(self, item):
        """
            Convert list items to python type.
        """
        item = evaluateValue(item)
        if isinstance(item, list):
            item = self.evaluateList(item)
        if isinstance(item, str):
            if (item.strip('-')).isnumeric():
                item = evaluateValue(item)
        return item

    def text(self):
        """
            Return single value or list value.
        """
        if len(self.selectedItems)==1:
            return self.evaluatePythonType(self.selectedItems[0])
        evaluatedItems = self.evaluateList(self.selectedItems)
        return evaluatedItems

    def updateOptions(self):
        """
            Update combobox options
        """
        self.edit.clear()
        self.edit.addItems(sorted(self.availableItems))

    def setValue(self, value):
        """
            Set pre-existing list value.
        """
        if not isinstance(value, list):
            value = [value]
        self.selectedItems = value
        self.showSelectedItems(self.selectedItems)
        if self.availableItems != None:
            for val in value:
                self.availableItems.remove(val)
            self.updateOptions()

    def getSelectedTag(self, title):
        """
            Create a selected item tag for showing the selected items.
        """
        group = QGroupBox()
        hlay = QHBoxLayout()
        hlay.setContentsMargins(2, 2, 2, 2)
        group.setLayout(hlay)

        itemLbl = QLabel(str(title))
        itemLbl.setAlignment(Qt.AlignCenter)
        hlay.addWidget(itemLbl)

        if self.isSingle:
            removeItem = QPushButton()
            removeItem.setIcon(qta.icon("fa.trash"))
            removeItem.setFixedSize(40, 25)
            removeItem.clicked.connect(
                lambda _, item=title: self.removeItem(item))
            hlay.addWidget(removeItem)
        else:
            self.removeFunction.append(lambda _, item=title: self.removeItem(item))

        return group

    def showSelectedItems(self, selItems):
        """
            Show a list of all the selected items.
        """
        pos = self.curr_index
        colLenght = 2 if self.isSingle else 0
        for item in selItems:
            tag = self.getSelectedTag(item)
            self.selectedWidgets.append(tag)
            self.selectedItemList.addWidget(tag, *pos)
            pos[1] += 1
            if pos[1] > colLenght:
                pos[1] = 0
                pos[0] += 1
        self.curr_index = pos

    def removeItem(self, item):
        """
            Remove an added item.
        """
        for wid in self.selectedWidgets:
            wid.deleteLater()
        self.selectedWidgets = []
        self.curr_index = [0, 0]
        self.selectedItems.remove(item)
        self.showSelectedItems(self.selectedItems)

        if self.availableItems != None:
            self.availableItems.append(item)
            self.updateOptions()

    def addItemFromCombobox(self):
        """
            Add an item from the combobox options.
        """
        selectedItem = self.edit.currentText()
        validSelectedItem = selectedItem and not selectedItem in self.selectedItems
        if validSelectedItem:
            self.selectedItems.append(selectedItem)
            self.showSelectedItems([selectedItem])

            self.availableItems.remove(selectedItem)
            self.updateOptions()
            return True
        return False

    def selectItem(self):
        """
            Add a new item to the list.
        """
        if self.availableItems != None:
            return self.addItemFromCombobox()
        elif self.isNumber:
            value = self.edit.value()
        else:
            value = self.edit.text()
            invalidStr = len(value)==0
            if invalidStr:
                return False
        self.selectedItems.append(value)
        self.showSelectedItems([value])
        return True

    def setTooltip(self, args):
        """
            Reimplement setTooltip function
        """
        return super().setToolTip(args)

    def getCombobox(self):
        wid = QComboBox()
        wid.setEditable(True)
        wid.completer().setCompletionMode(QCompleter.PopupCompletion)
        wid.setInsertPolicy(QComboBox.NoInsert)
        wid.addItems(sorted(self.availableItems))
        return wid

    def handleListWidget(self):
        """
            Show the correct input widget for the list type.
        """
        minWid = 50
        if self.availableItems != None:
            minWid = 100
            wid = self.getCombobox()
        elif self.isNumber:
            wid = handleSpinboxWidget(self.isNumber)
        else:
            wid = QLineEdit()
        wid.setMinimumWidth(minWid)

        return wid

    def _setupUi(self):
        glay = QGridLayout()

        self.edit = self.handleListWidget()
        glay.addWidget(self.edit, 0, 0, 1, 2)

        if self.isSingle:
            addBtn = QPushButton()
            addBtn.setFixedSize(40, 25)
            addBtn.setIcon(qta.icon("fa5s.plus"))
            addBtn.clicked.connect(self.selectItem)
            glay.addWidget(addBtn, 0, 2, 1, 1)

        self.selectedItemList = QGridLayout()
        self.selectedItemList.setContentsMargins(0, 0, 0, 0)
        self.selectedItemList.setSpacing(2)
        stretch = 3 if self.isSingle else 2
        glay.addLayout(self.selectedItemList, 1, 0, 2, stretch)

        self.setLayout(glay)
