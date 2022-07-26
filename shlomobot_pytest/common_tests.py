"""
This module contains test functions that are optional for the test files depending on question requirements
"""

# ================= IMPORTS =================

import re
import string
import inspect
import builtins
import dis
from types import FunctionType
from shlomobot_pytest.utils import (
    extract_functions_in_order,
    import_pyfile,
    get_functions_from_files,
    get_clean_function_lines,
    function_contains_regex,
    get_function_regex_matches,
    get_imported_modules,
)
from pathlib import Path
from importlib import import_module
from collections import defaultdict
import pep8
import pytest

# ================= CONSTANTS =================

WHILE_LOOP_REGEX = re.compile(r"while\s+.+")
WITH_OPEN_REGEX = re.compile(r"with\s+open\(['\"]")
FOR_LOOP_REGEX = re.compile(r"for\s+\w+\s+in\s+")
LAMBDA_REGEX = re.compile(r"lambda (?:[^\s]*? ?, ?)*?\w+\s*:")
ASSERT_REGEX = re.compile(r"^[ \t]*assert[ \t]*\w+")
INPUT_REGEX = re.compile(r"(^|[^\w\.])input\([\"']")

ABSOLUTE_PATH_REGEX_UNIX = re.compile(r"(r|f|rf|fr)?[\"'](/([^/ ]+ +)*[^/ ]+)+[\"']")
ABSOLUTE_PATH_REGEX_WINDOWS = re.compile(r"(r|f|rf|fr)?[\"'][A-Za-z]:([\\/]([^\ ]+ +)*[^\ ]+)+[\"']")
GLOBAL_DECLARATION_REGEX = re.compile(r"^[ \t]*global[ \t]+\w*(?:, *\w+)*(?=[ \t]*$)")
LIST_COMPREHENTION_REGEX = re.compile(
    r"\[\s*[\w\.\(\)'\"]+\s+(?:if .*? else [\w\.\(\)'\"]+\s+)?for\s+\w+\s+in\s+[\w\.\(\)'\"]+\s*(?:if .*)?\]"
)
OPEN_FILE_REGEX = re.compile(r"(\w*) = open\(")
CLOSE_FILE_REGEX = re.compile(r"(\w*)\.close\(\)")


def contains_name_eq_main_statement(py_filename: str) -> bool:
    """
    Checks if the "if __name__ == '__main__'" statement is present
    """
    module = import_pyfile(py_filename)
    module_code = inspect.getsource(module)

    # Check for __name__ == "__main__" statement
    name_eq_main_match = re.search(
        r"(?:if __name__\s?==\s?(?:'__main__'|\"__main__\")|if (?:'__main__'|\"__main__\")\s?==\s?__name__):",
        module_code,
    )
    return name_eq_main_match is not None


def is_main_function_last(py_filename: str) -> bool:
    """Checks if the 'main' function is the last function"""
    module = import_pyfile(py_filename)
    module_code = inspect.getsource(module)
    functions = extract_functions_in_order(module_code)

    # Check if file contains 'main' function and if it is last
    return functions[-1] == "main"


def find_functions_with_missing_docstrings(file_list: list[str]) -> list[str]:
    """
    Checks if the user created docstrings for all functions except 'main' function
    Returns a list of functions where docstrings are missing
    """

    functions_list = get_functions_from_files(file_list)

    func_missing_docstrings = []
    for function in functions_list:
        # Skip checking docstrings for 'main' function
        if function.__name__ == "main":
            continue
        # Handle missing docstrings
        if not function.__doc__:
            func_missing_docstrings.append(function.__name__)

    return func_missing_docstrings


def find_functions_with_single_quote_docstrings(file_list: list[str]) -> list[str]:
    """
    Check if the user created docstrings using double or single quotes
    Returns a list of functions where single quotes were used for docstrings
    """
    single_quote_docstrings = []
    functions_list = get_functions_from_files(file_list)

    for function in functions_list:
        # Skip checking docstrings for 'main' function
        if function.__name__ == "main":
            continue
        # Handle double quotes check if docstrings exist
        if function.__doc__:
            func_code = inspect.getsource(function)
            dbl_quotes_docstring = re.search(r"\"\"\"[\s\S]*?\"\"\"", func_code)
            if not dbl_quotes_docstring:
                single_quote_docstrings.append(function.__name__)

    return single_quote_docstrings


def contains_main_function(py_filename: str) -> bool:
    """
    Checks if the 'main' function exists within module
    """
    module = import_pyfile(py_filename)
    try:
        callable(getattr(module, "main"))
        return True
    except AttributeError:
        return False


def builtins_not_used_as_variable(function: FunctionType) -> bool:
    """
    Return True if no builtins are used as variables in the function, else return True
    """
    builtin_used_as_variable = r"^\s*(?:[^\s]*? ?, ?)*?{0} ?(?:\s*,\s*[^\W]+?\s*)*=.*"
    builtin_given_to_function = r"def {0}\((?:[^\s]*? ?, ?)*?{1}(?:\s*,\s*[^\W]+?)*\):"
    builtins_list = [
        word for word in dir(builtins) if word[0] not in string.ascii_uppercase + "_"
    ]

    # look for all possible builtin words used in the function
    for builtin_word in builtins_list:
        builtin_variable_regex = builtin_used_as_variable.format(builtin_word)
        builtin_paramater_regex = builtin_given_to_function.format(
            function.__name__, builtin_word
        )

        combined_builtin_regex = f"({builtin_paramater_regex}|{builtin_variable_regex})"

        if function_contains_regex(combined_builtin_regex, function):
            return False

    return True


def function_contains_global_variable(function: FunctionType) -> bool:
    """
    checks if in the function contains a global variable decleration
    """
    return function_contains_regex(GLOBAL_DECLARATION_REGEX, function)


def function_is_one_liner(py_filename: str, function_name: str) -> bool:
    """Checks if a given function is a one liner"""

    module = import_pyfile(py_filename)

    if hasattr(module, function_name):
        # Length is 2 since def line is also counted
        return len(get_clean_function_lines(getattr(module, function_name))) == 2

    return False


def correct_imports_are_made(py_filename: str, import_list: list[str]) -> bool:
    """
    Checks if all the required modules from import_list have been imported.
    This does not check if unnecessary modules are also imported.
    """
    imported_modules = get_imported_modules(py_filename)

    return all([module in imported_modules for module in import_list])


def check_test_function_exists_and_contains_asserts(py_filename: str) -> bool:
    """
    Checks that the module contains a test function that uses assert.

    The test function must be named `test`
    """

    module = import_pyfile(py_filename)
    try:
        test_function = getattr(module, "test")

        if not callable(test_function):
            return False

        return function_contains_regex(ASSERT_REGEX, test_function)
    except AttributeError:
        return False


def function_contains_input(function: FunctionType) -> bool:
    """
    Checks if a given function contains a call to the builtin
    `input` function

    Uses a regular expression to identify calls. This does
    not account for occurrences like the following, on which
    it would incorrectly return True:

    ```
    a = "input()"
    ```
    """
    # Get instructions from the generated bytecode of the function
    return function_contains_regex(INPUT_REGEX, function)


def function_contains_lambda(function: FunctionType) -> bool:
    return function_contains_regex(LAMBDA_REGEX, function)


def function_contains_for_loop(function: FunctionType) -> bool:
    return function_contains_regex(FOR_LOOP_REGEX, function)


def function_contains_with_open(function: FunctionType) -> bool:
    return function_contains_regex(WITH_OPEN_REGEX, function)


def function_contains_while_loop(function: FunctionType) -> bool:
    return function_contains_regex(WHILE_LOOP_REGEX, function)


def function_contains_absolute_paths(function: FunctionType) -> bool:
    return (
        function_contains_regex(ABSOLUTE_PATH_REGEX_UNIX, function)
        or function_contains_regex(ABSOLUTE_PATH_REGEX_WINDOWS, function)
    )


def function_contains_list_comprehention(function: FunctionType) -> bool:
    return function_contains_regex(LIST_COMPREHENTION_REGEX, function)


def every_opened_file_is_closed(function: FunctionType) -> bool:
    """
    Checks if a function closes all files it opens using open()

    This does not count files opened using with statements
    """

    # Get lines that open or close files
    open_file_lines = get_function_regex_matches(OPEN_FILE_REGEX, function)
    close_file_lines = get_function_regex_matches(CLOSE_FILE_REGEX, function)

    # Dict to record files that are opened but not close
    opened_file_variables: dict[str, int] = dict()

    # Populate dict with variables to opened files
    for line_content, line_number in open_file_lines:
        variable_name = re.search(OPEN_FILE_REGEX, line_content)[1]
        opened_file_variables[variable_name] = line_number
    
    # Remove variables that are closed after opening
    for line_content, line_number in close_file_lines:
        variable_name = CLOSE_FILE_REGEX.search(line_content)[1]
        if variable_name in opened_file_variables and opened_file_variables[variable_name] < line_number:
            del opened_file_variables[variable_name]
    
    # Return true if opened_file_variables is empty (no variables left unclosed)
    return not bool(opened_file_variables)


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