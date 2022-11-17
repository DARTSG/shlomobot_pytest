"""
This module contains test functions that are optional for the test files depending on question requirements
"""
from shlomobot_pytest.utils import (
    extract_functions_in_order,
    import_pyfile,
    get_functions_from_files,
    get_clean_function_lines,
    function_contains_regex,
)
from types import ModuleType, FunctionType
import builtins
import inspect
import re

GLOBAL_DECLERATION_REGEX = re.compile(r"\n\s*global\s+[^\W]+(?:\s*,\s*[^\W]+\s*)*\n")


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
        if function.__name__ == "main":
            continue
        # Handle double quotes check if docstrings exist
        if function.__doc__:
            func_code = inspect.getsource(function)
            dbl_quotes_docstring = re.search(r"\"\"\"[\s\S]*?\"\"\"", func_code)
            if not dbl_quotes_docstring:
                single_quote_docstrings.append(function_name)

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
    builtin_used_as_variable = r"\n\s*(?:[^\s]*? ?, ?)*?{0} ?(?:\s*,\s*[^\W]+?\s*)*=.*"
    builtin_given_to_function = r"def {0}\((?:[^\s]*? ?, ?)*?{1}(?:\s*,\s*[^\W]+?)*\):"
    builtins_list = [word for word in dir(builtins) if not re.match("[A-Z|_]", word[0])]

    function_name = function.__name__

    # look for all possible builtin words used in the function
    for builtin_word in builtins_list:
        builtin_variable_regex = builtin_used_as_variable.format(builtin_word)
        builtin_paramater_regex = builtin_given_to_function.format(
            function_name, builtin_word
        )

        if function_contains_regex(
            builtin_variable_regex, function
        ) or function_contains_regex(builtin_paramater_regex, function):
            return False

    return True


def function_contains_global_variable(function: FunctionType) -> bool:
    """
    checks if in the function contains a global variable decleration
    """
    return function_contains_regex(GLOBAL_DECLERATION_REGEX, function)


def function_is_one_liner(py_filename: str, function_name: str) -> bool:
    """Checks if a given function is a one liner"""

    module = import_pyfile(py_filename)

    if hasattr(module, function_name):
        # Length is 2 since def line is also counted
        return len(get_clean_function_lines(getattr(module, function_name))) == 2

    return False
