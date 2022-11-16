# ================= IMPORTS =================

import re
import sys
import pytest
import inspect
from io import StringIO
from typing import Generator
from importlib import import_module
from types import ModuleType, FunctionType

# ================= CONSTANTS =================

ONE_LINE_DOCSTRING_REGEX = r'^\t*\s*[\'"]+\w+[\'"]+'
OPEN_DOCSTRING_REGEX = r'^[\t\s]*?([\'"]+)'
CLOSE_DOCSTRING_REGEX = r'.*?([\'"]+)$'
COMMENT_REGEX = r"^\t*\s*#"
DEFINE_REGEX = r"^\s*def "


@pytest.fixture()
def simulate_python_io(monkeypatch, capsys: pytest.CaptureFixture):
    """
    A fixture to simulate input-output of a python file.
    This should be called with the python filename parameter, and than the input(s) as *args.
    Each given argument is equivalent to 1 line of input (splitted by \\n)
    """

    def wrapper(*args, pyfile):
        send_input_string = ""

        # Converting args to list, to maintain the order of the recived inputs.
        for item in args:
            send_input_string += str(item) + "\n"
        monkeypatch.setattr(sys, "stdin", StringIO(send_input_string))

        with open(pyfile, "r") as f:
            exec(f.read())
        user_output = capsys.readouterr().out
        return user_output

    return wrapper


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


def import_pyfile(module_name: str) -> ModuleType:
    """Extracts the module from a given filename"""
    stripped_module_name = module_name.removesuffix(".py")

    return import_module(stripped_module_name)


def get_functions_from_files(file_list: list[str]) -> Generator:
    """
    Extracts all functions from the files in file_list
    Creates a generator that returns a filename, FunctionType object pair
    """
    for filename in file_list:
        module = import_pyfile(filename)
        yield filename, extract_functions(module)


def get_clean_function_lines(function: FunctionType) -> list[str]:
    """Counts the amount on non comment or docstring lines in a function code"""

    clean_lines = []
    function_code = inspect.getsource(function)
    docstring_state = {"is_active": False, "value": ""}

    for line in function_code.splitlines():
        if (
            not re.search(COMMENT_REGEX, line)
            and not re.search(DEFINE_REGEX, line)
            and not re.search(ONE_LINE_DOCSTRING_REGEX, line)
        ):
            open_match = re.match(OPEN_DOCSTRING_REGEX, line)
            close_match = re.match(CLOSE_DOCSTRING_REGEX, line)

            if open_match and not docstring_state["is_active"]:
                docstring_state["is_active"] = True
                docstring_state["value"] = open_match.group()
            elif (
                close_match
                and docstring_state["is_active"]
                and (close_match.group() == docstring_state["value"])
            ):
                docstring_state["is_active"] = False
                docstring_state["value"] = ""
            elif not docstring_state["is_active"]:
                clean_lines.append(line)

    return clean_lines


def function_contains_regex(regex: str, function: FunctionType) -> bool:
    """Checks if the function contains a specific regular expression"""
    return any(
        [
            True if re.search(regex, line) else False
            for line in get_clean_function_lines(function)
        ]
    )
