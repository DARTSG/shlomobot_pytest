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
Parse the appropriate variable (list of filenames or whole dictionary) into the Pytest function and obtain the results as output
```python
functions_with_missing_docstrings = check_missing_docstrings(FILE_FUNCTION_MAP)
```

Full Test File Example
```python
from shlomobot_pytest.common_tests import check_missing_docstrings

FILE_FUNCTION_MAP = {"sample_test.py": ["main", "function1", "function2"]}

def test_for_missing_docstrings():
    functions_with_missing_docstrings = check_missing_docstrings(FILE_FUNCTION_MAP)
```

Library tested and works with Python 3.9.7