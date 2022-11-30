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
)

# ================= CONSTANTS =================

WHILE_LOOP_REGEX = re.compile(r"while\s+.+")
WITH_OPEN_REGEX = re.compile(r"with\s+open\(['\"]")
FOR_LOOP_REGEX = re.compile(r"for\s+\w+\s+in\s+\w+")
LAMBDA_REGEX = re.compile(r"lambda (?:[^\s]*? ?, ?)*?\w+\s*:")

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


def test_function_exists_and_contains_asserts(module_name: str) -> bool:
    """Checks that the tests function uses assert to test the function"""

    functions = get_functions_from_files([module_name])
    test_function = [
        function for function in functions if function.__name__ == "test"
    ]

    return len(test_function) > 0 and " assert " in inspect.getsource(test_function[0])


def function_contains_input(function: FunctionType) -> bool:
    """
    Checks if a given function contains a call to input

    Reads the bytecode of the function to find a direct call to
    the global input function. This does not check for calls like:

        a = input

        a()
    """
    # Get instructions from the generated bytecode of the function
    bytecode = dis.Bytecode(function)
    instructions = [instruction for instruction in bytecode]

    for line_number, instruction in enumerate(instructions):
        # Search for a CALL_FUNCTION instruction
        if instruction.opname == "CALL_FUNCTION":
            # Find the instruction that loads the called function
            load_instruction_line_number = line_number - instruction.arg - 1
            load_instruction = instructions[load_instruction_line_number]
        
            # Check if the load instruction loads the input function
            if load_instruction.opname == "LOAD_GLOBAL" and load_instruction.argval == "input":
                return True

    return False


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
