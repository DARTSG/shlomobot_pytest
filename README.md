# ShlomoBOT Pytest Library
This is a library that contains mainly pre-test functions for ShlomoBOT before the main code is checked and auto-graded.

## Pytest Library Functions
The list below consists of the functions that are currently within the ShlomoBOT Pytest library:
* find_missing_expected_files
* find_missing_expected_functions
* pep8_conformance
* contains_name_eq_main_statement
* is_main_function_last
* find_functions_with_missing_docstrings
* find_functions_with_single_quote_docstrings
* contains_main_function

# Usage
Import the necessary functions from the appropriate module
e.g. To check for missing docstrings within functions
```python
from shlomobot_pytest.common_tests import find_functions_with_missing_docstrings
```

Create a dictionary that contains the filename as the key and the list of function(s) to check within the file as the values
```python
FILE_FUNCTION_MAP = {"sample_test.py": ["main", "function1", "function2"]}
```

If applicable, assign a string with the name of the main submitted file to a variable
```python
MAIN_FILE_NAME = "main_sample_test.py"
```

Parse the appropriate variable (list of filenames or whole dictionary or main filename string) into the Pytest function and obtain the results as output (i.e. For `find_functions_with_missing_docstrings` function, it returns a list of functions that are missing docstrings)
```python
functions_with_missing_docstrings = find_functions_with_missing_docstrings(FILE_FUNCTION_MAP.keys())
```

Use the `create_custom_error_json` function to create a custom error message that will be raised if the results output contains errors as well as to calculate the number of points to be deducted. The function requires 4 parameters:
* feedback: The custom error message to be raised
* points_per_error: The number of points to deduct for every error detected
* max_points_deducted: The limit to the number of points to be deducted for a certain type of error
* number_of_errors: Total number of errors detected
```python
from shlomobot_pytest.utils import create_custom_error_json

feedback = f"The following function(s) are missing docstrings: {', '.join(functions_with_missing_docstrings)}!"
points_per_error = 10
max_points_deducted = 50
number_of_errors = len(functions_with_missing_docstrings)

custom_error_message = create_custom_error_json(feedback, points_per_error, max_points_deducted, number_of_errors)
```

Write asserts that checks for the results of the Pytest function and raise the custom error message if there are errors
```python
assert functions_with_missing_docstrings == [], custom_error_message
```

Full Test File Example
```python
from shlomobot_pytest.common_tests import find_functions_with_missing_docstrings
from shlomobot_pytest.utils import create_custom_error_json

FILE_FUNCTION_MAP = {"sample_test.py": ["main", "function1", "function2"]}
MAIN_FILE_NAME = "main_sample_test.py"

def test_for_missing_docstrings():
    functions_with_missing_docstrings = find_functions_with_missing_docstrings(FILE_FUNCTION_MAP.keys())

    feedback = f"The following function(s) are missing docstrings: {'/'.join(functions_with_missing_docstrings)}!"
    points_per_error = 10
    max_points_deducted = 50
    number_of_errors = len(functions_with_missing_docstrings)

    custom_error_message = create_custom_error_json(
        feedback, points_per_error, max_points_deducted, number_of_errors
    )

    assert functions_with_missing_docstrings == [], custom_error_message

def test_main_function():
    main_func_exists = contains_main_function(MAIN_FILE_NAME)

    feedback = "The 'main' function is missing!"
    points_per_error = 10
    max_points_deducted = 10
    number_of_errors = 1
    custom_error_message = create_custom_error_json(
        feedback, points_per_error, max_points_deducted, number_of_errors
    )

    assert main_func_exists, custom_error_message
```

Library tested and works with Python 3.9.7