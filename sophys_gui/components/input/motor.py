import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QGridLayout, QVBoxLayout
from sophys_gui.functions import getMotorInput, addLineJumps
from .list import SophysInputList


class SophysInputMotor(QWidget):

    def __init__(self, motorParameters, iterableInput):
        super().__init__()
        self.motorParameters = motorParameters
        self.iterableInput = iterableInput
        self.widList = []
        self._setupUi()

    def orderMotorValuesByRow(self, newValues):
        """
            Order args list value into attribute lists.
        """
        widQuant = len(self.widList)
        remId = 0
        valueList = []
        for idx, val in enumerate(newValues):
            isNewRow = idx>0 and idx%widQuant==0
            if isNewRow:
                remId += widQuant

            isNewColumn = remId == 0
            if isNewColumn:
                valueList.append([])

            itemCol = idx-remId
            valueList[itemCol].append(val)

        return valueList

    def addValueListToWidgets(self, valueList):
        """
            Set attribute value lists to the widgets.
        """
        removeRow = []
        rowLen = len(valueList[0])
        rowRange = range(0, rowLen)
        for idx, value in enumerate(valueList):
            currWid = self.widList[idx]
            currWid.setValue(value)
            newRow = idx == 0
            for idy in rowRange:
                if newRow:
                    removeRow.append([])
                removeRowFunct = currWid.removeFunction[idy]
                removeRow[idy].append(removeRowFunct)
        for idy in rowRange:
            self.addDeleteRow(removeRow[idy])

    def setValue(self, newValues):
        """
            Order the args values and set them to the list widgets.
        """
        valueList = self.orderMotorValuesByRow(newValues)
        self.addValueListToWidgets(valueList)

    def getWidgetValues(self):
        """
            Get values from the list widgets.
        """
        listResults = []
        for item in self.widList:
            listResults.append(item.text())
        return listResults

    def hasEmptyValue(self, listResults):
        """
            Verify if motor has empty parameter.
        """
        hasEmpty = False
        for result in listResults:
            if isinstance(result, list) and len(result) == 0:
                return True
        return hasEmpty

    def text(self):
        """
            Return motor list as a list.
        """
        listResults = self.getWidgetValues()
        if self.hasEmptyValue(listResults):
            return None
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
        """
            Delete a motor item in the GUI.
        """
        for deleteItem in deleteList:
            deleteItem(1)
        if deleteBtn:
            deleteBtn.deleteLater()

    def addDeleteRow(self, removeRow):
        """
            Add button for deleting an added motor.
        """
        deleteBtn = QPushButton("")
        deleteBtn.setFixedSize(40, 25)
        deleteBtn.setIcon(qta.icon("fa5s.trash-alt"))
        deleteBtn.clicked.connect(lambda _, delList=removeRow: self.deleteRow(delList, deleteBtn))
        self.btnsList.addWidget(deleteBtn)

    def selectValues(self):
        """
            Add motor inputs to the motor list.
        """
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

    def addMotorBtn(self):
        """
            Add button to add one motor.
        """
        vlay = QVBoxLayout()
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(5)

        addBtn = QPushButton()
        addBtn.setFixedSize(40, 25)
        addBtn.setIcon(qta.icon("fa5s.plus"))
        addBtn.clicked.connect(self.selectValues)
        vlay.addWidget(addBtn)
        return vlay

    def addMotorColumns(self, motorTyping, glay):
        """
            Dynamically add motor input widgets.
        """
        motorArray = motorTyping.split(";")
        motorTitles = motorArray[0].split(",")
        motorTooltip = motorArray[1].split(",")
        motorTypes = motorArray[2].split(",")

        col = 0
        for title, tooltip, argType in zip(motorTitles, motorTooltip, motorTypes):
            titleWid = QLabel(title)
            titleWid.setAlignment(Qt.AlignCenter)
            glay.addWidget(titleWid, 0, col)

            isNumber = any([item in argType for item in ["int", "float"]])
            if isNumber:
                isNumber = argType
            wid = self.iterableInput({"name":title}, isNumber, True)
            self.widList.append(wid)
            tooltipMsg = addLineJumps(tooltip)
            wid.setTooltip(tooltipMsg)
            glay.addWidget(wid, 1, col, 1, 1)
            col += 1


    def _setupUi(self):
        glay = QGridLayout(self)
        glay.setSpacing(2)
        glay.setContentsMargins(2, 2, 2, 2)

        motorTyping = getMotorInput(self.motorParameters)
        if motorTyping:
            self.addMotorColumns(motorTyping, glay)

            self.btnsList = self.addMotorBtn()
            argsQuant = glay.columnCount() + 1
            glay.addLayout(self.btnsList, 1, argsQuant, 1, 1)
        else:
            listInput = SophysInputList(None, False)
            glay.addWidget(listInput)
