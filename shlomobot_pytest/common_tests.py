"""
This module contains test functions that are optional for the test files depending on question requirements
"""

from importlib import import_module

from shlomobot_pytest.utils import (
    extract_functions,
    extract_functions_in_order,
)
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


def correct_imports_are_made(module_name: str, import_list: list[str]) -> bool:
    """Checks if the sutdent imported all the required modules from import_list"""
    stripped_module_name = module_name.removesuffix(".py")
    module = import_module(stripped_module_name)
    module_code = inspect.getsource(module)

    modules_list = re.findall(r"import (\w+)", module_code)

    return all([True if module in modules_list else False for module in import_list])
