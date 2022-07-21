import pep8
from importlib import import_module
from typing import Dict, List, Union


class Pep8ConformanceFailException(Exception):
    pass


def check_user_file(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, str, None]]:
    """
    Check if the user submitted the correct file name

    Returns a dict consisting of error and filename that was wrongly named
    """
    for filename in file_function_dict.keys():
        try:
            file = filename.rstrip(".py")
            import_module(file)
        except ImportError:
            return {"error": False, "filename": filename}
    return {"error": True, "filename": None}


def check_user_function(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, str, None]]:
    """
    Check if function in user submitted code is correctly named

    Returns a dict consisting of error, function that was wrongly named
    and filename where function is located in
    """
    for filename, functions in file_function_dict.items():
        try:
            file = filename.rstrip(".py")
            user_file = import_module(file)
            for function in functions:
                callable(getattr(user_file, function))
        except AttributeError:
            return {"error": False, "filename": filename, "function": function}
    return {"error": True, "filename": None, "function": None}


def pep8_conformance(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[bool, int]]:
    """
    Test that we conform to PEP8.

    Returns a dict consisting of error and total number of Pep8 errors
    """
    filenames = file_function_dict.keys()
    pep8style = pep8.StyleGuide()
    result = pep8style.check_files(filenames)
    if result.total_errors != 0:
        print("Found code style errors (and warnings).")
        return {"error": False, "total_errors": result.total_errors}
    return {"error": True, "total_errors": 0}
