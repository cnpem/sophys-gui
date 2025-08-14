from typing import Literal
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, \
    QLineEdit, QComboBox


BLUESKY_AUTOSAVE_METADATA = {
    "metadata_save_file_location": {
        "type": str,
        "tooltip": "The path to save the metadata to (not including the file name)."
    },
    "metadata_save_file_identifier": {
        "type": str,
        "tooltip": "The file name to use for saving the metadata, without the suffix. If not set, it will use the run's UID (defined as the start document's UID)."
    },
    "metadata_save_file_format": {
        "type": Literal,
        "enum": ["JSON,NEXUS", "NEXUS", "JSON", "SPEC"],
        "tooltip": "The file format to use for saving the metadata. If not set, it will use the JSON format. Available options are defined in the aforementioned file. You can also specify multiple formats separated by comma, and all the options will be used."
    },
    "metadata_save_increment_disable": {
        "type": Literal,
        "enum": ["True", "False"],
        "tooltip": "If present, this disables using a 'scan id'-like logic to create file names when the identifier is customized and would normally override the previous file with the same name."
    },
    "beamline_name": {
        "type": str,
        "tooltip": "The name of the source beamline the data is coming from. Used as a metadata inside the NeXus file, but also to mount the default path on Ibira for data_schema_file_path if it hasn't been set."
    },
    "experiment_stage": {
        "type": str,
        "tooltip": "The name of the experiment stage in which the data was collected."
    },
    "experimental_technique": {
        "type": str,
        "default": "",
        "tooltip": "The acronym of the experimental technique being performed. Currently, it is just an additional metadata but in the future it will be of great importance for the operation."
    },
    "data_schema_file_path": {
        "type": str,
        "default": "",
        "tooltip": "If set, defines the path to the data schema file instead of using the default one at Ibira, which is based on beamline_name."
    }
}


class SophysMetadataForm(QDialog):

    def __init__(self, metadata_updater, md_widget):
        super().__init__()
        self.inputs = {}
        self.metadata_values = metadata_updater()
        self.global_metadata_updater = metadata_updater
        self.md_widget = md_widget
        self._setupUi()

    def getDialogBtns(self):
        """
            Create the form dialog buttons.
        """
        btns = QDialogButtonBox()
        btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self.saveMetadata)
        btns.rejected.connect(self.reject)
        return btns
    
    def saveMetadata(self):
        autosave_metadata = self.getValues()
        self.global_metadata_updater(autosave_metadata)
        metadata = self.md_widget.text()
        metadata.update(autosave_metadata)
        self.md_widget.setValue(metadata)
        self.accept()

    def getValues(self):
        values = {}
        for title, wid in self.inputs.items():
            if isinstance(wid, QLineEdit):
                values[title] = wid.text()
                if len(values[title]) == 0:
                    if "default" in BLUESKY_AUTOSAVE_METADATA[title]:
                        del values[title]
            else:
                values[title] = wid.currentText()
        return values

    def _setupUi(self):
        glay = QGridLayout(self)

        for idx, (title, widget_spec) in enumerate(BLUESKY_AUTOSAVE_METADATA.items()):
            wid_title = QLabel(title)
            glay.addWidget(wid_title, idx, 0)

            if widget_spec["type"] == str:
                input_wid = QLineEdit()
                if title in self.metadata_values:
                    input_wid.setText(self.metadata_values[title])
            else:
                input_wid = QComboBox()
                input_wid.addItems(widget_spec["enum"])
                if title in self.metadata_values:
                    input_wid.setCurrentText(self.metadata_values[title])
            self.inputs[title] = input_wid
            glay.addWidget(input_wid, idx, 1)

        glay.addWidget(self.getDialogBtns(), idx+1, 0, 1, 2)