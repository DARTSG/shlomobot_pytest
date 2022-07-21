from importlib import import_module

from shlomobot_pytest.utils import find_functions
import inspect
import re
from typing import Dict, List, Union


def check_name_main_statement(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, List]]:
    """
    Check if the "if __name__ == '__main__'" statement is present

    Returns a dict consisting of error and error count 1 if the statement is absent in all files
    """
    statement_present_files = []
    results = {"error": True, "error_count": 0}
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
        results["error"] = False
        results["error_count"] = 1
    return results


def check_main_func_order(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, List]]:
    """
    Check if the 'main' function is the last function

    Returns a dict consisting of error and list of filenames where main func is not the last
    """
    filenames = []
    results = {"error": True, "filenames": filenames}
    for filename in file_function_dict.keys():
        file = filename.rstrip(".py")
        user_file = import_module(file)
        functions = find_functions(user_file)
        if functions[-1] != "main":
            filenames.append(filename)
    if filenames:
        results["error"] = False
    return results


def check_missing_docstrings(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, List]]:
    """
    Check if the user created docstrings for all functions except 'main' function

    Returns a dict consisting of error and list of functions where docstrings are missing
    """
    func_missing_docstrings = []
    results = {
        "error": True,
        "missing_docstrings": func_missing_docstrings,
    }
    for filename in file_function_dict.keys():
        file = filename.rstrip(".py")
        user_file = import_module(file)
        # Find the list of functions within the file
        functions = find_functions(user_file)
        for function in functions:
            # Skip checking docstrings for 'main' function
            if function.__name__ == "main":
                pass
            # Handle missing docstrings
            elif not function.__doc__:
                func_missing_docstrings.append(function.__name__)

    if func_missing_docstrings:
        results["error"] = False
    return results


def check_single_quote_docstrings(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, List]]:
    """
    Check if the user created docstrings using double or single quotes

    Returns a dict consisting of error and list of functions where single quotes were used for docstrings
    """
    single_quote_docstrings = []
    results = {
        "error": True,
        "single_quote_docstr": single_quote_docstrings,
    }
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
            elif function.__doc__:
                func_code = inspect.getsource(function)
                dbl_quotes_docstring = re.search(r"\"\"\"[\s\S]*?\"\"\"", func_code)
                if not dbl_quotes_docstring:
                    single_quote_docstrings.append(function.__name__)

    if single_quote_docstrings:
        results["error"] = False
    return results


def check_main_function(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, List]]:
    """
    Check if the user created a 'main' function

    Returns a dict consisting of error and error count 1 if main function is absent in all files
    """
    main_func_present = []
    results = {"error": True, "error_count": 0}
    for filename in file_function_dict.keys():
        try:
            file = filename.rstrip(".py")
            user_file = import_module(file)
            callable(getattr(user_file, "main"))
            main_func_present.append(filename)
        except AttributeError:
            pass
    if not main_func_present:
        results["error"] = False
        results["error_count"] = 1
    return results
