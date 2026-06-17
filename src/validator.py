from typing import Any

from src.models import FunctionCallOutput, FunctionDefinition, JsonType


def is_valid_type(value: Any, expected_type: JsonType) -> bool:
    """Check whether a value matches an expected JSON type.

    Args:
        value: The value to check.
        expected_type: One of the JSON type literals.

    Returns:
        True if `value` matches `expected_type`, otherwise False.
    """
    if expected_type == "string":
        return isinstance(value, str)

    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type == "boolean":
        return isinstance(value, bool)

    return False


def validate_output(
    output: FunctionCallOutput,
    functions: list[FunctionDefinition],
) -> bool:
    """Validate a FunctionCallOutput against function definitions.

    Args:
        output: The function call output to validate.
        functions: Available function definitions to validate against.

    Returns:
        True if `output` matches a function signature and types, else False.
    """
    selected_function = None

    for function in functions:
        if function.name == output.name:
            selected_function = function
            break

    if selected_function is None:
        return False

    expected_parameters = set(selected_function.parameters.keys())
    actual_parameters = set(output.parameters.keys())

    if expected_parameters != actual_parameters:
        return False

    for parameter_name, parameter_info in selected_function.parameters.items():
        value = output.parameters[parameter_name]

        if not is_valid_type(value, parameter_info.type):
            return False

    return True
