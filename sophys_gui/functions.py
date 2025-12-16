import qtawesome as qta
import os as _os
import yaml
import ast
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QPushButton, QDoubleSpinBox, \
    QSpinBox


def getItemRecursively(original_obj: object, attrs: list):
    """
        Get item in a dictionary using a list.
    """
    _prev = original_obj
    for attr in attrs:
        if isinstance(attr, list):
            concAttr = []
            for item in attr:
                concAttr.append(getItemRecursively(_prev, [item]))
            _prev = concAttr
        else:
            if attr in _prev:
                _prev = getattr(_prev, attr, _prev[attr])
            else:
                return ''
    return _prev


def getHeader(text):
    """
        Get table header.
    """
    title = QLabel(text)
    title.setAlignment(Qt.AlignCenter)
    title.setFixedHeight(60)
    title.setStyleSheet(
        """
            font-weight: 800;
            font-size: 18px;
        """
    )

    return title

def getFilePath(file_path):
    """
        Get the absolute path for files inside the sophys gui package.
    """
    abspath = _os.path.abspath(_os.path.dirname(__file__))
    admin_file = _os.path.join(abspath, file_path)
    return admin_file

def evaluateValue(value):
    """
        Evaluate a string value to a python type.
    """
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except Exception:
            print("Eval error - ", value)
    return value

def createSingleBtn(btnDict, runEngine):
    """
        Create simple button.
    """
    title = btnDict["title"]
    btn = QPushButton(title)
    btn.clicked.connect(
        lambda _, cmd=btnDict["cmd"], re=runEngine: cmd(re))
    btn.setIcon(qta.icon(btnDict["icon"]))
    return btn

def addArgsToKwargs(argsList):
    """
        Concatenate arguments and keyword arguments.
    """
    args = argsList[0].copy()
    argsList[1]["detectors"] = args.pop(0)
    argsList[1]["args"] = args

def getMotorInput(paramMeta):
    separator = "-.-"
    motorDescription = paramMeta["description"]
    motorTypeIndex = motorDescription.index(separator)
    if motorTypeIndex:
        motorTyping = motorDescription[motorTypeIndex:].replace(separator, "")
        return motorTyping
    return None


def handleSpinboxWidget(valueType):
    """
        Handle int and float spinbox widgets.
    """
    isFloat = valueType == 'float'
    if isFloat:
        spinbox = QDoubleSpinBox()
        spinbox.setSingleStep(0.001)
        spinbox.setDecimals(4)
    else:
        spinbox = QSpinBox()
    spinbox.setMaximumHeight(50)
    spinbox.setMinimum(-10**8)
    spinbox.setMaximum(10**8)
    return spinbox


def addLineJumps(message):
    """
        Break lines in tooltips.
    """
    lineSize = 30
    newMsg = ""
    if "\n" in message:
        return message
    msgArray = message.split(" ")
    while len(msgArray) > 0:
        newLine = ""
        for msgLine in msgArray:
            newLine += msgArray.pop(0)
            if len(newLine) > lineSize:
                newLine += "\n"
                break
            newLine += " "
        newMsg += newLine
    return newMsg

def openYaml(yml_file_path):
    if yml_file_path:
        with open(yml_file_path, "r") as f:
                config = yaml.safe_load(f)

        return config
    return {}
