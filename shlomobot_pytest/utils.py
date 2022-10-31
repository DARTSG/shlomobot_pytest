import inspect
import re
from types import ModuleType, FunctionType
import pytest
import sys
from io import StringIO

@pytest.fixture()
def simulate_input_output(monkeypatch, capsys: pytest.CaptureFixture):
    """
    A fixture to simulate input-output of a python file.
    This should be called with the filename parameter, and than the input(s) as *args.
    Each given argument is equivalent to 1 line of input (splitted by \\n)
    """

    def _internal(filename="", *args):
        send_input_string = ""
        
        # Converting args to list, to maintain the order of the recived inputs.
        for item in args:
            send_input_string += str(item) + "\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(send_input_string))

        with open(filename, 'r') as f:
            exec(f.read())
        user_output = capsys.readouterr().out
        return user_output

    return _internal


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
    points_per_error: int,
    max_points_deducted: int,
    number_of_errors: int,
    feedback: str,
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
