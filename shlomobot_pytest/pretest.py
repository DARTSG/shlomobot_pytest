import pep8
from importlib import import_module
from typing import Dict, List, Union


def check_user_file(file_list: List[str]) -> List:
    """
    Check if the user submitted the correct file name

    Returns a list of filenames that were wrongly named
    """
    wrongly_named_files = []
    for filename in file_list:
        try:
            file = filename.rstrip(".py")
            import_module(file)
        except ImportError:
            wrongly_named_files.append(filename)

    return wrongly_named_files


def check_user_function(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[str, None]]:
    """
    Check if function in user submitted code is correctly named

    Returns a dict consisting of function(s) that was wrongly named
    """
    wrongly_named_functions = []
    for filename, functions in file_function_dict.items():
        try:
            file = filename.rstrip(".py")
            user_file = import_module(file)
            for function in functions:
                callable(getattr(user_file, function))
        except AttributeError:
            wrongly_named_functions.append(function)
    return wrongly_named_functions


def pep8_conformance(file_list: List[str]) -> Dict[str, List[str]]:
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
    errors = {}
    pep8style = pep8.StyleGuide()
    for file in file_list:
        result = pep8style.check_files([file])
        if result.total_errors != 0:
            error_messages = []
            for error in result._deferred_print:
                error_message = f"Row {error[0]}: Col {error[1]}: {error[2]} {error[3]}"
                error_messages.append(error_message)
            errors[result.filename] = error_messages

    return errors
