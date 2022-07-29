from importlib import import_module

from shlomobot_pytest.utils import find_functions, extract_functions_in_order
import inspect
import re
from typing import Dict, List


def check_name_main_statement(file_function_dict: Dict[str, List[str]]) -> bool:
    """
    Check if the "if __name__ == '__main__'" statement is present

    Returns a boolean whether the __name__ == '__main__' statement exists or not
    """
    statement_present_files = []
    name_main_statement_exists = True
    for filename in file_function_dict.keys():
        file = filename.rstrip(".py")
        user_file = import_module(file)
        file_code = inspect.getsource(user_file)

        # Check for __name__ == "__main__" statement
        name_main_line = re.search(
            r"(?:if __name__\s?==\s?(?:'__main__'|\"__main__\")|if (?:'__main__'|\"__main__\")\s?==\s?__name__):",
            file_code,
        )
        if name_main_line:
            statement_present_files.append(filename)
    if not statement_present_files:
        name_main_statement_exists = False
    return name_main_statement_exists


def check_main_func_order(file_function_dict: Dict[str, List[str]]) -> List:
    """
    Check if the 'main' function is the last function

    Returns a list of filenames where main func is present but not the last
    """
    filenames = []
    for filename in file_function_dict.keys():
        file = filename.rstrip(".py")
        user_file = import_module(file)
        file_code = inspect.getsource(user_file)
        functions = extract_functions_in_order(file_code)

        # Check if file contains 'main' function and if it is last
        if functions:
            for function in functions:
                if function == "main" and functions[-1] != function:
                    filenames.append(filename)

    return filenames


def check_missing_docstrings(file_function_dict: Dict[str, List[str]]) -> List:
    """
    Check if the user created docstrings for all functions except 'main' function

    Returns a list of functions where docstrings are missing
    """
    func_missing_docstrings = []
    for filename in file_function_dict.keys():
        file = filename.rstrip(".py")
        user_file = import_module(file)
        # Find the list of functions within the file
        functions = find_functions(user_file)
        for function in functions:
            # Skip checking docstrings for 'main' function
            if function.__name__ == "main":
                continue
            # Handle missing docstrings
            if not function.__doc__:
                func_missing_docstrings.append(function.__name__)

    return func_missing_docstrings


def check_single_quote_docstrings(file_function_dict: Dict[str, List[str]]) -> List:
    """
    Check if the user created docstrings using double or single quotes

    Returns a list of functions where single quotes were used for docstrings
    """
    single_quote_docstrings = []
    for filename in file_function_dict.keys():
        file = filename.rstrip(".py")
        user_file = import_module(file)
        # Find the list of functions within the file
        functions = find_functions(user_file)
        for function in functions:
            # Skip checking docstrings for 'main' function
            if function.__name__ == "main":
                pass
            # Handle double quotes check if docstrings exist
            if function.__doc__:
                func_code = inspect.getsource(function)
                dbl_quotes_docstring = re.search(r"\"\"\"[\s\S]*?\"\"\"", func_code)
                if not dbl_quotes_docstring:
                    single_quote_docstrings.append(function.__name__)

    return single_quote_docstrings


def check_main_function(file_function_dict: Dict[str, List[str]]) -> int:
    """
    Check if the user created a 'main' function

    Returns a boolean whether the 'main' function exists or not
    """
    main_func_present = []
    main_function_exists = True
    for filename in file_function_dict.keys():
        try:
            file = filename.rstrip(".py")
            user_file = import_module(file)
            callable(getattr(user_file, "main"))
            main_func_present.append(filename)
        except AttributeError:
            pass
    if not main_func_present:
        main_function_exists = False

    return main_function_exists
