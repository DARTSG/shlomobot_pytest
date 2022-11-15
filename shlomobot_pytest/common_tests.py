"""
This module contains test functions that are optional for the test files depending on question requirements
"""

from importlib import import_module

from shlomobot_pytest.utils import (
    extract_functions,
    extract_functions_in_order,
)
import builtins
import inspect
import re


def contains_name_eq_main_statement(module_name: str) -> bool:
    """
    Checks if the "if __name__ == '__main__'" statement is present
    """
    stripped_module_name = module_name.removesuffix(".py")
    module = import_module(stripped_module_name)
    module_code = inspect.getsource(module)

    # Check for __name__ == "__main__" statement
    name_eq_main_match = re.search(
        r"(?:if __name__\s?==\s?(?:'__main__'|\"__main__\")|if (?:'__main__'|\"__main__\")\s?==\s?__name__):",
        module_code,
    )
    return name_eq_main_match is not None


def is_main_function_last(module_name: str) -> bool:
    """Checks if the 'main' function is the last function"""
    stripped_module_name = module_name.removesuffix(".py")
    module = import_module(stripped_module_name)
    module_code = inspect.getsource(module)
    functions = extract_functions_in_order(module_code)

    # Check if file contains 'main' function and if it is last
    return functions[-1] == "main"


def find_functions_with_missing_docstrings(file_list: list[str]) -> list[str]:
    """
    Checks if the user created docstrings for all functions except 'main' function

    Returns a list of functions where docstrings are missing
    """
    func_missing_docstrings = []
    for filename in file_list:
        stripped_module_name = filename.removesuffix(".py")
        module = import_module(stripped_module_name)
        # Find the list of functions within the file
        functions = extract_functions(module)
        for function in functions:
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
    for filename in file_list:
        stripped_module_name = filename.removesuffix(".py")
        module = import_module(stripped_module_name)
        # Find the list of functions within the file
        functions = extract_functions(module)
        for function in functions:
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


def contains_main_function(module_name: str) -> bool:
    """
    Checks if the 'main' function exists within module
    """
    stripped_module_name = module_name.removesuffix(".py")
    module = import_module(stripped_module_name)
    try:
        callable(getattr(module, "main"))
        return True
    except AttributeError:
        return False


def builtins_not_used_as_variable(file_list: list[str]) -> bool:
    """
    Checks if inside the files given in 'file_list' any builtins are used as variables

    Return True if no builtins are used as variables, False if at least one is.
    """
    builtins_list = dir(builtins)[80:]

    builtin_used_as_variable = r"\n\s*(?:[^\s]*? ?, ?)*?{0} ?(?:\s*,\s*[^\W]+?\s*)*=.*"
    builtin_given_to_function = r"def {0}\((?:[^\s]*? ?, ?)*?{1}(?:\s*,\s*[^\W]+?)*\):"

    for filename in file_list:
        stripped_module_name = filename.removesuffix(".py")
        module = import_module(stripped_module_name)
        # Find the list of functions within the file
        functions = extract_functions(module)
        for function in functions:
            # extract function code
            function_code = inspect.getsource(function)
            # look for all possible builtin words used in the function
            for builtin_word in builtins_list:
                builtin_as_variable_regex = builtin_used_as_variable.format(
                    builtin_word
                )
                builtin_as_paramater_regex = builtin_given_to_function.format(
                    function.__name__, builtin_word
                )
                occurences_as_variable = re.search(
                    builtin_as_variable_regex, function_code
                )
                occurences_as_paramater = re.search(
                    builtin_as_paramater_regex, function_code
                )
                if occurences_as_variable or occurences_as_paramater:
                    return False

    return True


def declared_global_variable(file_list: list[str]) -> bool:
    """
    checks if in the code of the files inside file_list there was decleration of a global variable
    """
    global_variable_declared = False
    global_decleration_regex = r"\n\s*global\s+[^\W]+(?:\s*,\s*[^\W]+\s*)*\n"

    for filename in file_list:
        stripped_module_name = filename.removesuffix(".py")
        module = import_module(stripped_module_name)
        # Find the list of functions within the file
        functions = extract_functions(module)
        for function in functions:
            function_code = inspect.getsource(function)
            if re.search(global_decleration_regex, function_code):
                global_variable_declared = True

    return global_variable_declared
