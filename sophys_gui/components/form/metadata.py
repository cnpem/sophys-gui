from typing import Literal


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
        "type": Literal["NEXUS", "JSON", "SPEC"],
        "default": "NEXUS",
        "tooltip": "The file format to use for saving the metadata. If not set, it will use the JSON format. Available options are defined in the aforementioned file. You can also specify multiple formats separated by comma, and all the options will be used."
    },
    "metadata_save_increment_disable": {
        "type": bool,
        "default": None,
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