from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QCompleter


class SophysComboBox(QComboBox):

    def __init__(self, run_engine, inputType: str):
        super().__init__()
        self.run_engine = run_engine
        self.options_list = []
        self._setupUi(inputType)

    def getAvailableDevicesType(self, title):
        """
            Get the key for searching the devices options.
        """
        optionsMode = {
            "__MOVABLE__": "is_movable",
            "__READABLE__": "is_readable",
            "__FLYABLE__": "is_flyable"
        }
        for device_type, http_server_key in optionsMode.items():
            if device_type in title:
                return http_server_key
        return None

    def getDevicesOptions(self, availableDevices):
        """
            Get all the available devices based on one of its property.
        """
        allowedDevices = self.run_engine._allowed_devices
        optionsList = []
        for key, device in allowedDevices.items():
            if device[availableDevices]:
                optionsList.append(key)
        return optionsList
    
    def updateOptions(self):
        self.clear()
        self.addItems(sorted(self.options_list))

    def _setupUi(self, inputType):
        self.setEditable(True)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        insert_mode = QComboBox.InsertAlphabetically if "str" in inputType else QComboBox.NoInsert
        self.setInsertPolicy(insert_mode)

        availableDevices = self.getAvailableDevicesType(inputType)
        if "bool" in inputType:
            self.options_list = ["True", "False"]
        elif "Literal" in inputType:
            literal_idx = inputType.index("Literal")
            splitStr = inputType[literal_idx+8:].replace(" '", "").replace("'", "")
            options_end_idx = splitStr.index("]")
            self.options_list = splitStr[:options_end_idx].split(",")
        elif availableDevices:
            optionsList = self.getDevicesOptions(availableDevices)
            self.options_list = optionsList
        self.addItems(sorted(self.options_list))