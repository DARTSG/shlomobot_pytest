import inspect
import re
from types import ModuleType, FunctionType


def extract_functions(module: ModuleType) -> list[FunctionType]:
    """
    Find a list of functions present within file
    """
    functions = []
    for _, func in inspect.getmembers(module, inspect.isfunction):
        if func.__module__ == module.__name__:
            functions.append(func)

    return functions


def extract_functions_in_order(file_code: str) -> list[str]:
    """
    Find a list of function strings within a file while keeping its original order
    """
    functions = re.findall(r"def ([\s\S]+?)\([\s\S]*?\)", file_code)

    return functions


def create_custom_error_json(
    feedback: str,
    points_per_error: int,
    max_points_deducted: int,
    number_of_errors: int,
) -> str:
    """Creates a custom error message for the test files"""

    total_points_deducted = calculate_total_deducted_score(
        points_per_error,
        max_points_deducted,
        number_of_errors,
    )

    return f'{{"feedback": "{feedback}", "points_deducted": {total_points_deducted}}} EndMarker'


def calculate_total_deducted_score(
    points_per_error: int, max_points_deducted: int, number_of_errors: int
) -> int:
    """Calculates the total number of points to be deducted"""
    total_points_deducted = points_per_error * number_of_errors

    return min(total_points_deducted, max_points_deducted)
