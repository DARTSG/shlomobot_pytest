# ================= IMPORTS =================

import re
import sys
import pytest
import inspect
import dis
from io import StringIO
from typing import Iterator
from importlib import import_module
from black import format_str, FileMode
from types import ModuleType, FunctionType

# ================= CONSTANTS =================

ONE_LINE_DOCSTRING_REGEX = re.compile(r'^[ \t]*("""|\'\'\').*(\1)[ \t]*$')
OPEN_DOCSTRING_REGEX = re.compile(r'^[\t\s]*?([\'"]{3})')
CLOSE_DOCSTRING_REGEX = re.compile(r'.*?([\'"]{3})$')
COMMENT_REGEX = re.compile(r"^\t*\s*#")
DEFINE_REGEX = re.compile(r"^\s*def ")
TEMP_FILENAME = "studentfile_temp.py"


@pytest.fixture()
def simulate_python_io(monkeypatch, capsys: pytest.CaptureFixture):
    """
    A fixture to simulate input-output of a python file.
    This should be called with the python filename parameter, and than the input(s) as *args.
    Each given argument is equivalent to 1 line of input (splitted by \\n)
    """

    def wrapper(*args, pyfile):
        send_input_string = ""

        # Converting args to list, to maintain the order of the recived inputs.
        for item in args:
            send_input_string += str(item) + "\n"
        monkeypatch.setattr(sys, "stdin", StringIO(send_input_string))

        with open(pyfile, "r") as f:
            exec(f.read())
        user_output = capsys.readouterr().out
        return user_output

    return wrapper


def convert_pyfile_to_function_type(py_filename: str):
    """
    Takes the python file that do not contain a function and converts it into a function.
    This function returns the FunctionType.

    Take Note when using this function:
    1) Import the TEMP_FILENAME constant
    2) Include a teardown function in the test file to remove the created temp file

    Example:
    def teardown_function():
        os.remove(TEMP_FILENAME)
    """

    trainee_source_code = ""
    trainee_function_name = "trainee_function"
    indentation = "    "

    with open(py_filename, "r") as f:
        for each_line in f.readlines():
            trainee_source_code += (indentation + each_line)

    trainee_source_code = (f"def {trainee_function_name}():\n{trainee_source_code}")

    with open(TEMP_FILENAME, "w") as w:
        w.write(trainee_source_code)

    from studentfile_temp import trainee_function

    return trainee_function


def extract_functions(module: ModuleType) -> list[FunctionType]:
    """
    Find a list of functions present within file
    """
    functions = []
    for _, func in inspect.getmembers(module, inspect.isfunction):
        if func.__module__ == module.__name__:
            functions.append(func)

    return functions


def extract_functions_in_order(file_code: str) -> list[str]:
    """
    Find a list of function strings within a file while keeping its original order
    """
    functions = re.findall(r"def ([\s\S]+?)\([\s\S]*?\)", file_code)

    return functions


def create_custom_error_json(
    points_per_error: int,
    max_points_deducted: int,
    number_of_errors: int,
    feedback: str,
) -> str:
    """Creates a custom error message for the test files"""

    total_points_deducted = calculate_total_deducted_score(
        points_per_error,
        max_points_deducted,
        number_of_errors,
    )

    return f'{{"feedback": "{feedback}", "points_deducted": {total_points_deducted}}} EndMarker'


def calculate_total_deducted_score(
    points_per_error: int, max_points_deducted: int, number_of_errors: int
) -> int:
    """Calculates the total number of points to be deducted"""
    total_points_deducted = points_per_error * number_of_errors

    return min(total_points_deducted, max_points_deducted)


def import_pyfile(py_filename: str) -> ModuleType:
    """Extracts the module from a given filename"""
    stripped_module_name = py_filename.removesuffix(".py")

    return import_module(stripped_module_name)


def get_functions_from_files(file_list: list[str]) -> Iterator[FunctionType]:
    """
    Extracts all functions from the files in file_list
    Creates a generator that returns a filename, FunctionType object pair
    """
    for py_filename in file_list:
        module = import_pyfile(py_filename)
        for function in extract_functions(module):
            yield function


def get_clean_function_lines(function: FunctionType, should_black=True) -> list[str]:
    """Count the amount on non comment or docstring lines in a function code"""
    function_code = inspect.getsource(function)

    # Reformats file to connect split lines using black
    if should_black:
        function_code = format_str(function_code, mode=FileMode(line_length=99999))

    # Using filter to remove empty lines from the list of lines
    split_code = list(filter(lambda line: line.strip(), function_code.splitlines()))

    # The first line will be the definition of the function
    clean_lines = [split_code[0]]
    docstring_type = ""

    for line_num, line in enumerate(split_code[1:]):
        # Do not count commented line or single line docstring
        if not re.search(COMMENT_REGEX, line) and not re.search(
            ONE_LINE_DOCSTRING_REGEX, line
        ):
            # Check for opening multi-line docstring in the start of the code
            if line_num == 0:
                open_match = re.match(OPEN_DOCSTRING_REGEX, line)
                if open_match:
                    docstring_type = open_match.group()
                else:
                    clean_lines.append(line)
            else:
                # From second line onward, when no docstring is active add lines to the list
                if docstring_type == "":
                    clean_lines.append(line)
                # Check for closing of multi-line docstring second line onward
                else:
                    close_match = re.match(CLOSE_DOCSTRING_REGEX, line)
                    if close_match and (close_match.group() == docstring_type):
                        docstring_type = ""

    return clean_lines


def function_contains_regex(regex: str | re.Pattern, function: FunctionType) -> bool:
    """Checks if the function contains a specific regular expression"""
    if isinstance(regex, re.Pattern):
        regex = re.compile(regex)

    for line in get_clean_function_lines(function):
        if re.search(regex, line):
            return True

    return False


def get_function_regex_matches(regex: str | re.Pattern, function: FunctionType) -> list[tuple[str, int]]:
    """
    Returns a tuple (line content, line number) for each match
    of the given regex in the given function's body. The line number
    is the original
    """
    if isinstance(regex, re.Pattern):
        regex = re.compile(regex)

    cleaned_lines = get_clean_function_lines(function)

    return [(line, index + 1) for index, line in enumerate(cleaned_lines) if re.search(regex, line)]


def get_imported_modules(py_filename: str) -> set[str]:
    """
    Returns a set of imported modules in the python file.

    This includes modules imported using the `import` and
    `from` keywords. For example, given a file with:

    ```py
    from math import sqrt
    import re, os
    ...
    ```

    The function will return the set `{"math", "re", "os"}`
    """
    
    module = import_pyfile(py_filename)

    bytecode = dis.Bytecode(inspect.getsource(module))
    instructions = [instruction for instruction in bytecode]

    imported_modules = set()

    for _, instruction in enumerate(instructions):
        # Search for a IMPORT_NAME instruction
        if instruction.opname == "IMPORT_NAME":
            import_name = instruction.argval
            imported_modules.add(import_name)

    return imported_modules


def function_calls_other_function(monkeypatch: pytest.fixture, function: FunctionType, *function_strings: str) -> dict[str, bool]:
    """
    Checks if the `function` calls other imported functions

    `function_strings` are dot separated import strings in the `module.function` format, for example:

    ```py
    "builtins.input"
    "AnswerModule.test"
    ```
    """
    # Record to be modified
    record = dict()

    # Intervening function that modifies the record and runs the original function
    def record_and_run_wrapper(original_function, function_string):
        def record_and_run(*args, **kwargs):
            nonlocal record
            record[function_string] = True
            return original_function(*args, **kwargs)
        return record_and_run

    for function_string in function_strings:
        print(function_string)
        other_module_name, other_function_name = function_string.split(".")
        original_function = import_module(other_module_name).__dict__[other_function_name]

        if not callable(original_function):
            raise TypeError(f"{function_string} is not a callable function")

        record[function_string] = False

        # Monkeypatch the called_function
        monkeypatch.setattr(function_string, record_and_run_wrapper(original_function, function_string))

    # Call the function
    function()

    return record
