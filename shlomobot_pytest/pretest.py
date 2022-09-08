"""This module contains test functions that are primarily needed for all test files"""

from collections import defaultdict
import pep8
from importlib import import_module
from pathlib import Path


def find_missing_expected_files(file_list: list[str]) -> list[str]:
    """
    Check if the user submitted the correct file name

    Returns a list of filenames that were wrongly named
    """
    wrongly_named_files = []
    for filename in file_list:
        try:
            if filename.endswith(".py"):
                # If its a python file try to import it
                python_module = filename.removesuffix(".py")
                import_module(python_module)
            else:
                # If not just make sure it exists
                if not Path(filename).exists():
                    wrongly_named_files.append(filename)
        except ImportError:
            wrongly_named_files.append(filename)

    return wrongly_named_files


def find_missing_expected_functions(
    expected_functions_map: dict[str, list[str]]
) -> list[str]:
    """
    Check if all of the expected functions in the submitted python file exist

    expected_functions_map is a dictionary mapping file names to a list of
    expected functions in that file

    Returns a list of all missing functions
    """
    wrongly_named_functions = []
    for filename, functions in expected_functions_map.items():
        if not filename.endswith(".py"):
            raise ValueError("We can only check for functions in python modules")

        python_module = filename.removesuffix(".py")
        user_file = import_module(python_module)
        for function in functions:
            try:
                callable(getattr(user_file, function))
            except AttributeError:
                wrongly_named_functions.append(function)

    return wrongly_named_functions


def pep8_conformance(file_list: list[str]) -> dict[str, list[str]]:
    """
    Test that we conform to PEP8.

    Returns a dictionary with the filename as key and list of Pep8 error comments as values
    e.g. errors = {
        "sample_test.py":
        [
            "Row 9: Col 30: 'E201' whitespace after '('",
            "Row 9: Col 71: 'E202' whitespace before ')'"
        ]
    }
    """
    errors = defaultdict(list)
    pep8style = pep8.StyleGuide()

    # We loop and test the files for pep8 conformance one by one because otherwise
    # we won't be able to map errors to the file they came from
    for python_module in file_list:
        result = pep8style.check_files([python_module])
        if result.total_errors != 0:
            for row, column, error_code, error_message, _ in result._deferred_print:
                errors[result.filename].append(
                    f"Row {row}: Col {column}: {error_code} {error_message}"
                )

    return errors
