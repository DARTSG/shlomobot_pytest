import inspect
import re
from types import ModuleType
from typing import Dict, List, Union


def find_functions(file: ModuleType) -> List:
    """
    Returns the list of functions within a file

    :param file: file module (product of import_module)
    :type file: module
    """
    functions = [
        fn
        for _, fn in inspect.getmembers(file, inspect.isfunction)
        if fn.__module__ == file.__name__
    ]
    return functions


def extract_functions_in_order(file_code: str) -> List:
    """
    Returns a list of functions within a file in original order
    """
    functions = re.findall(r"def ([\s\S]+?)\([\s\S]*?\)", file_code)

    return functions


def create_custom_error_json(
    custom_variables: Dict[str, Union[str, int]],
) -> str:
    """Returns a constructed custom error message"""

    total_points_deducted = calculate_total_deducted_score(
        custom_variables["points_per_error"],
        custom_variables["max_points_deducted"],
        custom_variables["number_of_errors"],
    )
    custom_error_message = f'{{"feedback": "{custom_variables["feedback"]}", "points_deducted": {total_points_deducted}}} EndMarker'

    return custom_error_message


def calculate_total_deducted_score(
    points_per_error: int, max_points_deducted: int, number_of_errors: int
) -> int:
    """Returns the total number of points to be deducted"""
    total_points_deducted = points_per_error * number_of_errors
    if total_points_deducted > max_points_deducted:
        total_points_deducted = max_points_deducted

    return total_points_deducted
