"""
This module contains test functions that are optional for the test files depending on question requirements
"""
from shlomobot_pytest.utils import (
    extract_functions_in_order,
    import_pyfile,
    get_functions_from_files,
)
import builtins
import inspect
import re


def contains_name_eq_main_statement(module_name: str) -> bool:
    """
    Checks if the "if __name__ == '__main__'" statement is present
    """
    module = import_pyfile(module_name)
    module_code = inspect.getsource(module)

    # Check for __name__ == "__main__" statement
    name_eq_main_match = re.search(
        r"(?:if __name__\s?==\s?(?:'__main__'|\"__main__\")|if (?:'__main__'|\"__main__\")\s?==\s?__name__):",
        module_code,
    )
    return name_eq_main_match is not None


def is_main_function_last(module_name: str) -> bool:
    """Checks if the 'main' function is the last function"""
    module = import_pyfile(module_name)
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
    for function_name, function in functions_list:
        # Skip checking docstrings for 'main' function
        if function_name == "main":
            continue
        # Handle missing docstrings
        if not function.__doc__:
            func_missing_docstrings.append(function_name)

    return func_missing_docstrings


def find_functions_with_single_quote_docstrings(file_list: list[str]) -> list[str]:
    """
    Check if the user created docstrings using double or single quotes

    Returns a list of functions where single quotes were used for docstrings
    """
    single_quote_docstrings = []
    functions_list = get_functions_from_files(file_list)

    for function_name, function in functions_list:
        # Skip checking docstrings for 'main' function
        if function_name == "main":
            continue
        # Handle double quotes check if docstrings exist
        if function.__doc__:
            func_code = inspect.getsource(function)
            dbl_quotes_docstring = re.search(r"\"\"\"[\s\S]*?\"\"\"", func_code)
            if not dbl_quotes_docstring:
                single_quote_docstrings.append(function_name)

    return single_quote_docstrings


def contains_main_function(module_name: str) -> bool:
    """
    Checks if the 'main' function exists within module
    """
    module = import_pyfile(module_name)
    try:
        callable(getattr(module, "main"))
        return True
    except AttributeError:
        return False
