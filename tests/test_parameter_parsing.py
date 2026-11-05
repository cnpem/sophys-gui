import collections
import logging
import typing

import pytest

from qtpy.QtWidgets import QLineEdit

from sophys_gui.components.form.parameter_parsing import (
    get_python_type_from_annotation,
    is_bool,
    is_device,
    is_float,
    is_integer,
    is_iterable,
    is_literal,
    is_mapping, get_widget_for_parameter,
)


@pytest.fixture(scope="session", autouse=True)
def configure_logger():
    logger = logging.getLogger("sophys.ema.components.parameters")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s %(levelname)s - %(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    yield


@pytest.mark.parametrize(
    [
        "type_variable",
        "_is_mapping",
        "_is_iterable",
        "_is_device",
        "_is_literal",
        "_is_bool",
        "_is_integer",
        "_is_float",
    ],
    [
        (dict[str, typing.Literal["A", "B"]], True, False, False, False, False, False, False),  # fmt: off
        (list[float], False, True, False, False, False, False, False),
        (typing.Literal["A", "B", "C"], False, False, False, True, False, False, False),
        (bool, False, False, False, False, True, False, False),
        (bool | None, False, False, False, False, True, False, False),
        (int, False, False, False, False, False, True, False),
        (int | None, False, False, False, False, False, True, False),
        (float, False, False, False, False, False, False, True),
        (float | None, False, False, False, False, False, False, True),
        (collections.abc.Hashable, False, False, False, False, False, False, False),
    ],
)
def test_type_checks(
    type_variable: type,
    _is_mapping: bool,
    _is_iterable: bool,
    _is_device: bool,
    _is_literal: bool,
    _is_bool: bool,
    _is_integer: bool,
    _is_float: bool,
):
    assert is_mapping(type_variable) == _is_mapping
    assert is_iterable(type_variable) == _is_iterable
    assert is_device(type_variable) == _is_device
    assert is_literal(type_variable) == _is_literal
    assert is_bool(type_variable) == _is_bool
    assert is_integer(type_variable) == _is_integer
    assert is_float(type_variable) == _is_float


@pytest.mark.parametrize(
    [
        "annotation",
        "type_variable",
    ],
    [
        ("dict[str, typing.Any]", dict[str, typing.Any]),
        ("typing.Sequence[int]", list[int]),
        ("__READABLE__", typing.Annotated[typing.Any, "__READABLE__"]),
        ("__MOVABLE__", typing.Annotated[typing.Any, "__MOVABLE__"]),
        ("Literal['A', 'B', 'C']", typing.Literal["A", "B", "C"]),
        ("bool", bool),
        ("bool | None", bool | None),
        ("int", int),
        ("int | None", int | None),
        ("float", float),
        ("float | None", float | None),
        ("Hashable", collections.abc.Hashable),
    ],
)
def test_python_type_from_annotation(annotation: str, type_variable: type):
    assert get_python_type_from_annotation(annotation) == type_variable


run_engine_model_sentinel = object()


@pytest.mark.parametrize(
    [
        "parameter_information",
        "expected_class",
        "expected_args",
    ],
    [
        ({"name": "test_widget", "annotation": {"type": "str"}}, QLineEdit, {}),
    ],
)
def test_widgets_from_parameter_information(parameter_information: dict, expected_class: type, expected_args: dict, qapp):
    title_widget, result_class, result_args = get_widget_for_parameter(parameter_information["name"], parameter_information, run_engine_model=run_engine_model_sentinel)

    assert result_class is expected_class
    for argument_name, expected_argument_value in expected_args.items():
        assert argument_name in result_args
        assert result_args[argument_name] == expected_argument_value

