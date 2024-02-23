import os as _os
import qtawesome as qta
import ast
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QPushButton

def getItemRecursively(original_obj: object, attrs: list):
    _prev = original_obj
    for attr in attrs:
        if attr in _prev:
            _prev = getattr(_prev, attr, _prev[attr])
        else:
            return ''
    return _prev


def getHeader(text):
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
        Get the absolute path for files inside the sapoti package.
    """
    abspath = _os.path.abspath(_os.path.dirname(__file__))
    admin_file = _os.path.join(abspath, file_path)
    return admin_file

def getLoadingButton():
    loading = QPushButton('')
    loading.setIcon(qta.icon(
        'fa5s.spinner', animation=qta.Spin(loading)))
    loading.setVisible(False)
    loading.setFlat(True)
    return loading

def evaluateValue(value):
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except Exception:
            print("Eval error - ", value)
    return value
