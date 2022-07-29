# ShlomoBOT Pytest Library
This is a library that contains mainly pre-test functions for ShlomoBOT before the main code is checked and auto-graded.

## Pytest Library Functions
The list below consists of the functions that are currently within the ShlomoBOT Pytest library:
* check_user_file
* check_user_function
* pep8_conformance
* check_name_main_statement
* check_main_func_order
* check_missing_docstrings
* check_single_quote_docstrings
* check_main_function

# Usage
Import the necessary functions from the appropriate module
e.g. To check for missing docstrings within functions
```python
from shlomobot_pytest.common_tests import check_missing_docstrings
```

Create a dictionary that contains the filename as the key and the list of function(s) to check within the file as the values
```python
FILE_FUNCTION_MAP = {"sample_test.py": ["main", "function1", "function2"]}
```

Parse the appropriate variable (list of filenames or whole dictionary) into the Pytest function and obtain the results as output (i.e. For 'check_missing_docstrings' function, it returns a list of functions that are missing docstrings)
```python
functions_with_missing_docstrings = check_missing_docstrings(FILE_FUNCTION_MAP)
```

Use the 'create_custom_error_json' function to create a custom error message that will be raised if the results output contains errors as well as to calculate the number of points to be deducted
The function requires 4 parameters:
* feedback: The custom error message to be raised
* points_per_error: The number of points to deduct for every error detected
* max_points_deducted: The limit to the number of points to be deducted for a certain type of error
* number_of_errors: Total number of errors detected
```python
feedback = f"Use double quotes for docstrings for the following function(s): {'/'.join(functions_with_missing_docstrings)}!"
points_per_error = 10
max_points_deducted = 50
number_of_errors = len(functions_with_missing_docstrings)

custom_error_message = create_custom_error_json(feedback, points_per_error, max_points_deducted, number_of_errors)
```

Write asserts that checks for the results of the Pytest function and raise the custom error message if there are errors
```python
assert functions_with_missing_docstrings, custom_error_message
```

Full Test File Example
```python
from shlomobot_pytest.common_tests import check_missing_docstrings
from shlomobot_pytest.utils import create_custom_error_json

FILE_FUNCTION_MAP = {"sample_test.py": ["main", "function1", "function2"]}

def test_for_missing_docstrings():
    functions_with_missing_docstrings = check_missing_docstrings(FILE_FUNCTION_MAP)

    feedback = f"The following function(s) are missing docstrings: {'/'.join(functions_with_missing_docstrings)}!"
    points_per_error = 10
    max_points_deducted = 50
    number_of_errors = len(functions_with_missing_docstrings)

    custom_error_message = create_custom_error_json(
        feedback, points_per_error, max_points_deducted, number_of_errors
    )

    assert functions_with_missing_docstrings, custom_error_message
```

Library tested and works with Python 3.9.7