import pep8
from importlib import import_module
from typing import Dict, List, Union


def check_user_file(file_list: List[str]) -> List:
    """
    Check if the user submitted the correct file name

    Returns a list of filenames that were wrongly named
    """
    filenames = []
    for filename in file_list:
        try:
            file = filename.rstrip(".py")
            import_module(file)
        except ImportError:
            filenames.append(filename)

    return filenames


def check_user_function(
    file_function_dict: Dict[str, List[str]]
) -> Dict[str, Union[str, None]]:
    """
    Check if function in user submitted code is correctly named

    Returns a dict consisting of function that was wrongly named
    and filename where function is located in
    """
    for filename, functions in file_function_dict.items():
        try:
            file = filename.rstrip(".py")
            user_file = import_module(file)
            for function in functions:
                callable(getattr(user_file, function))
        except AttributeError:
            return {"filename": filename, "function": function}
    return {"filename": None, "function": None}


def pep8_conformance(file_function_dict: Dict[str, List[str]]) -> int:
    """
    Test that we conform to PEP8.

    Returns the total number of Pep8 errors detected
    """
    filenames = file_function_dict.keys()
    pep8style = pep8.StyleGuide()
    result = pep8style.check_files(filenames)
    if result.total_errors != 0:
        print("Found code style errors (and warnings).")
    return result.total_errors
