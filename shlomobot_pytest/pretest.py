"""This module contains test functions that are primarily needed for all test files"""

from collections import defaultdict
import pep8
from importlib import import_module
from pathlib import Path

from shlomobot_pytest.utils import create_custom_error_json

from shlomobot_pytest.common_tests import contains_main_function

from functools import partial

def register_tests(file_function_map, test_contains_main_function=None):
    """
    Currently only implemented for test_contains_main_function.

    The way to call this function is this:

    - If there is no change to the feedback and points.

    register_tests(
        FILE_FUNCTION_MAP,
        test_contains_main_function={}
    )


    - If there is are changes to the feedback and points.
    register_tests(
        FILE_FUNCTION_MAP,
        test_contains_main_function={
            "feedback":"Main function where?",
            "points_per_error":11,
            "max_points_deducted":11,
            "number_of_errors":2,
        }
    )

    """
    if test_contains_main_function is not None:
        new_test_contains_main_function = partial(test_contains_main_function_default, file_function_map, **test_contains_main_function)
        new_test_contains_main_function()


def find_missing_expected_files(file_list: list[str]) -> list[str]:
    """
    Check if the user submitted the correct file name

    Returns a list of filenames that were wrongly named
    """
    wrongly_named_files = []
    for filename in file_list:
        if not Path(filename).exists():
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


def test_contains_main_function_default(
    FILE_FUNCTION_MAP=dict(),
    feedback="Where is your main() function?",
    points_per_error=10,
    max_points_deducted=10,
    number_of_errors=1,
):
    # Check that the code contains the main() function

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in FILE_FUNCTION_MAP.keys():
        assert contains_main_function(filename), custom_error_message