import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QComboBox, \
    QPushButton, QGridLayout, QGroupBox, QHBoxLayout


class SophysInputList(QWidget):

    def __init__(self, itemList):
        super().__init__()
        self.selectedItems = []
        self.selectedWidgets = []
        self.availableItems = itemList
        self.curr_index = [0, 0]
        self._setupUi()

    def getSelectedTag(self, title):
        group = QGroupBox()
        hlay = QHBoxLayout()
        hlay.setContentsMargins(2, 2, 2, 2)
        group.setLayout(hlay)

        itemLbl = QLabel(title)
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

        self.availableItems.append(item)
        self.cb.clear()
        self.cb.addItems(self.availableItems)

    def selectItem(self):
        selectedItem = self.cb.currentText()
        if selectedItem and not selectedItem in self.selectedItems:
            self.selectedItems.append(selectedItem)
            self.showSelectedItems([selectedItem])

            self.availableItems.remove(selectedItem)
            self.cb.clear()
            self.cb.addItems(self.availableItems)

    def _setupUi(self):
        glay = QGridLayout()
        glay.setContentsMargins(2, 2, 2, 2)
        glay.setSpacing(2)

        self.cb = QComboBox()
        self.cb.addItems(self.availableItems)
        glay.addWidget(self.cb, 0, 0, 1, 2)

        add_btn = QPushButton()
        add_btn.setIcon(qta.icon("fa5s.plus"))
        add_btn.clicked.connect(self.selectItem)
        glay.addWidget(add_btn, 0, 2, 1, 1)

        self.selectedItemList = QGridLayout()
        self.selectedItemList.setContentsMargins(0, 0, 0, 0)
        self.selectedItemList.setSpacing(2)
        glay.addLayout(self.selectedItemList, 1, 0, 2, 3)

        self.setLayout(glay)
