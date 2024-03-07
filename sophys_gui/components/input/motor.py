import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QGridLayout, QVBoxLayout
from sophys_gui.functions import getMotorInput
from .list import SophysInputList


class SophysInputMotor(QWidget):

    def __init__(self, motorParameters, iterableInput):
        super().__init__()
        self.motorParameters = motorParameters
        self.iterableInput = iterableInput
        self.widList = []
        self._setupUi()

    def setValue(self, newValues):
        widQuant = len(self.widList)
        remId = 0
        valueList = []
        for idx, val in enumerate(newValues):
            if idx>0 and idx%widQuant==0:
                remId += widQuant
            if remId == 0:
                valueList.append([])
            itemId = idx-remId
            valueList[itemId].append(val)
        removeRow = []
        for idx, value in enumerate(valueList):
            currWid = self.widList[idx]
            currWid.setValue(value)
            for idy, val in enumerate(value):
                if idx == 0:
                    removeRow.append([])
                removeRow[idy].append(currWid.removeFunction[idy])
        for idy, _ in enumerate(valueList[0]):
            self.addDeleteRow(removeRow[idy])

    def text(self):
        listResults = []
        for item in self.widList:
            listResults.append(item.text())
        orderedResults = []
        max = len(listResults[0]) if isinstance(listResults[0], list) else 1
        if max > 1:
            for resultId in range(0, max):
                newResults = [resList[resultId] for resList in listResults]
                orderedResults.extend(newResults)
        else:
            orderedResults = listResults
        return orderedResults

    def deleteRow(self, deleteList, deleteBtn):
        for deleteItem in deleteList:
            deleteItem(1)
        if deleteBtn:
            deleteBtn.deleteLater()

    def addDeleteRow(self, removeRow):
        deleteBtn = QPushButton("")
        deleteBtn.setFixedSize(40, 25)
        deleteBtn.setIcon(qta.icon("fa5s.trash-alt"))
        deleteBtn.clicked.connect(lambda _, delList=removeRow: self.deleteRow(delList, deleteBtn))
        self.btnsList.addWidget(deleteBtn)

    def selectValues(self):
        removeRow = []
        for item in self.widList:
            returnedStatus = item.selectItem()
            if returnedStatus:
                removeRow.append(item.removeFunction[-1])
            else:
                self.deleteRow(removeRow, None)
                removeRow = []
                break
        if len(removeRow) > 0:
            self.addDeleteRow(removeRow)

    def _setupUi(self):
        glay = QGridLayout(self)
        glay.setSpacing(2)
        glay.setContentsMargins(2, 2, 2, 2)
        motorTyping = getMotorInput(self.motorParameters)
        if motorTyping:
            motorArray = motorTyping.split(";")
            motorTitles = motorArray[0].split(",")
            motorTooltip = motorArray[1].split(",")
            motorTypes = motorArray[2].split(",")

            for idy, title in enumerate(motorTitles):
                titleWid = QLabel(title)
                titleWid.setAlignment(Qt.AlignCenter)
                glay.addWidget(titleWid, 0, idy)

                isNumber = any([item in motorTypes[idy] for item in ["int", "float"]])
                if isNumber:
                    isNumber = motorTypes[idy]
                wid = self.iterableInput({"name":title}, isNumber, True)
                self.widList.append(wid)
                wid.setTooltip(motorTooltip[idy])
                glay.addWidget(wid, 1, idy, 1, 1)

            self.btnsList = QVBoxLayout()
            self.btnsList.setContentsMargins(0, 0, 0, 0)
            self.btnsList.setSpacing(5)

            addBtn = QPushButton()
            addBtn.setFixedSize(40, 25)
            addBtn.setIcon(qta.icon("fa5s.plus"))
            addBtn.clicked.connect(self.selectValues)
            self.btnsList.addWidget(addBtn)

            glay.addLayout(self.btnsList, 1, len(motorTitles)+1, 1, 1)
        else:
            glay.addWidget(SophysInputList(None, False))
