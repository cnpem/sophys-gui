import collections
import importlib
import logging
import numbers
import typing

from pydantic import TypeAdapter, ValidationError
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QLineEdit, QWidget

from sophys_gui.components.input.combobox import SophysComboBox
from sophys_gui.components.input.dictionary import SophysInputDict
from sophys_gui.components.input.list import SophysInputList
from sophys_gui.components.input.motor import SophysInputMotor
from sophys_gui.components.input.spinbox import SophysSpinBox

from .util import UNKNOWN_TYPES

logger = logging.getLogger("sophys.gui.components.parameters")


def is_mapping(type_variable: type) -> bool:
    try:
        TypeAdapter(type_variable).validate_python({})
    except ValidationError:
        return False
    return True


def is_iterable(type_variable: type) -> bool:
    try:
        TypeAdapter(type_variable).validate_python([])
    except ValidationError:
        return False
    return True


def is_device(type_variable: type) -> bool:
    try:
        _annotation = type_variable.__metadata__  # ty: ignore
        return _annotation in UNKNOWN_TYPES
    except AttributeError:
        return False
    return True


def is_literal(type_variable: type) -> bool:
    return (
        "literal" in str(type_variable).lower()
        and not is_mapping(type_variable)
        and not is_iterable(type_variable)
    )


def is_bool(type_variable: type) -> bool:
    try:
        TypeAdapter(type_variable).validate_python(True, strict=True)

        # HACK: Avoid common bool protocols (e.g. Hashable)
        if type_variable in collections.abc.__dict__.values():
            return False
    except ValidationError:
        return False
    return True


def is_integer(type_variable: type) -> bool:
    try:
        if not isinstance(TypeAdapter(type_variable).validate_python(0, strict=True), numbers.Integral):
            return False

        # HACK: Avoid common bool protocols (e.g. Hashable)
        if type_variable in collections.abc.__dict__.values():
            return False
    except ValidationError:
        return False
    return True


def is_float(type_variable: type) -> bool:
    try:
        if isinstance(TypeAdapter(type_variable).validate_python(0.0, strict=True), numbers.Integral):
            return False

        # HACK: Avoid common bool protocols (e.g. Hashable)
        if type_variable in collections.abc.__dict__.values():
            return False
    except ValidationError:
        return False
    return True


def is_parameter_required(parameter_information: dict) -> bool:
    return "default" not in parameter_information


def get_python_type_from_annotation(annotation: str) -> type:
    environment = {
        "typing": importlib.import_module("typing"),
        "collections.abc": importlib.import_module("collections.abc"),
        "NoneType": type(None),
    }

    environment.update(environment["typing"].__dict__)
    environment.update(environment["collections.abc"].__dict__)

    for original_name, transformed_name in UNKNOWN_TYPES.items():
        annotation = annotation.replace(original_name, transformed_name)

    logger.debug("Attempting to parse '%s' as a Python type...", annotation)
    try:
        return eval(annotation, environment)
    except Exception as exc:
        logger.exception("Failed to parse annotation '%s' as a valid Python type.", annotation, exc_info=exc)

        return typing.Any

def get_widget_for_parameter(parameter_name: str, parameter_information: dict, *, run_engine_model) -> tuple[QLabel, type[QWidget], dict]:
    is_required = is_parameter_required(parameter_information)

    widget_title = parameter_name + (" (required)" if is_required else "")
    widget_title_widget = QLabel(widget_title)
    widget_title_widget.setMaximumHeight(50)
    widget_title_widget.setAlignment(Qt.AlignCenter)

    parameter_type_str = parameter_information.get("annotation", {}).get("type", "typing.Any")
    parameter_type = get_python_type_from_annotation(parameter_type_str)

    widget_ctor_arguments = {}

    widget_type = QLineEdit
    if is_mapping(parameter_type):
        logger.debug("Parameter '%s' is a mapping.", parameter_name)
        widget_type = SophysInputDict
    elif "-.-" in parameter_information.get("description", ""):
        logger.debug("Parameter '%s' is a motor list.", parameter_name)
        widget_type = SophysInputMotor
        widget_ctor_arguments = {"run_engine": run_engine_model, "motorParameters": parameter_information, "iterableInput": SophysInputList}
    elif is_iterable(parameter_type):
        logger.debug("Parameter '%s' is a input list.", parameter_name)
        widget_type = SophysInputList
        widget_ctor_arguments = {"run_engine": run_engine_model, "inputType": parameter_type_str if "motor" not in parameter_name else "__MOVABLE__"}
    elif is_device(parameter_type) or is_literal(parameter_type) or is_bool(parameter_type):
        logger.debug("Parameter '%s' is a combo box.", parameter_name)
        widget_type = SophysComboBox
        widget_ctor_arguments = {"run_engine": run_engine_model, "inputType": parameter_type_str if "motor" not in parameter_name else "__MOVABLE__"}
    elif is_integer(parameter_type) or is_float(parameter_type):
        logger.debug("Parameter '%s' is a spin box.", parameter_name)
        widget_type = SophysSpinBox
        widget_ctor_arguments = {"valueType": "int" if is_integer(parameter_type) else "float", "isRequired": is_required}

    return widget_title_widget, widget_type, widget_ctor_arguments
