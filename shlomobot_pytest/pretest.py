"""This module contains test functions that are primarily needed for all test files"""
import pytest

from functools import partial
from types import FunctionType

from shlomobot_pytest.utils import create_custom_error_json

from shlomobot_pytest.common_tests import (
    find_missing_expected_files,
    find_missing_expected_functions,
    pep8_conformance,
    contains_main_function,
    contains_name_eq_main_statement,
    is_main_function_last,
    find_functions_with_missing_docstrings,
)


def pytest_decorate(name: str, depends: list[str], function: FunctionType):
    """
    This function is used to decorate the pretest with the pytest decorators
    """
    
    @pytest.mark.dependency(
        name=name, depends=depends,
    )
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


def register_tests(
    module_scope: dict[str, str],
    file_function_map: dict[str, list[str]]=None,
    test_expected_files_exist: dict[str, str | int]=None,
    test_expected_functions_exist: dict[str, str | int]=None,
    test_pep8_compliant: dict[str, str | int]=None,
    test_contains_main_function: dict[str, str | int]=None,
    test_name_eq_main_statement_exist: dict[str, str | int]=None,
    test_main_function_is_last_function: dict[str, str | int]=None,
    test_docstring_exists: dict[str, str | int]=None,
):
    """
    This function helps to perform the pretests for each test file

    Notes:
    - This function allows flexibility by allowing the test writer to choose whatever test he/she wants.
    - The first three tests (test_expected_files_exist, test_expected_functions_exist, test_pep8_compliant) just need to ={}
    - The other tests allows the test writer to change the feedback and points deducted. They can either change one or all.

    Sample for calling this function:
    register_tests(
        globals(),
        file_function_map,
        test_expected_files_exist={},
        test_expected_functions_exist={},
        test_pep8_compliant={},
        test_contains_main_function={
            "feedback":"Main function where?",
            "points_per_error":11,
            "max_points_deducted":11,
            "number_of_errors":2,
        },
        test_name_eq_main_statement_exist={
            "feedback":"Name = Main where?",
            "points_per_error":12,
            "max_points_deducted":12,
        },
        test_main_function_is_last_function={
            "feedback":"Why your main not last?",
        },
        test_docstring_exists={
            "feedback":"Docstring Where??",
        },
    )

    When adding new pretests, things to do:
    1) Add the test name as one of the parameter in the register_tests function
    2) Add a if condition inside the function to create a partial function
    3) Add the new pretest function into the code and end the function name with '_pretest'
    """

    if test_expected_files_exist is not None:
        pytest_name = "test_expected_files_exist"
        pytest_depends = []

        module_scope['test_expected_files_exist'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_expected_files_exist_pretest, file_function_map, **test_expected_files_exist)
        )

    if test_expected_functions_exist is not None:
        pytest_name = "test_expected_functions_exist"
        pytest_depends = ["test_expected_files_exist"]

        module_scope['test_expected_functions_exist'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_expected_functions_exist_pretest, file_function_map, **test_expected_functions_exist)
        )

    if test_pep8_compliant is not None:
        pytest_name = "test_pep8_compliant"
        pytest_depends = ["test_expected_functions_exist"]

        module_scope['test_pep8_compliant'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_pep8_compliant_pretest, file_function_map, **test_pep8_compliant)
        )

    if test_contains_main_function is not None:
        pytest_name = "test_contains_main_function"
        pytest_depends = ["test_expected_functions_exist"]

        module_scope['test_contains_main_function'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_contains_main_function_pretest, file_function_map, **test_contains_main_function)
        )

    if test_name_eq_main_statement_exist is not None:
        pytest_name = "test_name_eq_main_statement_exist"
        pytest_depends = ["test_contains_main_function"]

        module_scope['test_name_eq_main_statement_exist'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_name_eq_main_statement_exist_pretest, file_function_map, **test_name_eq_main_statement_exist)
        )

    if test_main_function_is_last_function is not None:
        pytest_name = "test_main_function_is_last_function"
        pytest_depends = ["test_contains_main_function"]

        module_scope['test_main_function_is_last_function'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_main_function_is_last_function_pretest, file_function_map, **test_main_function_is_last_function)
        )

    if test_docstring_exists is not None:
        pytest_name = "test_docstring_exists"
        pytest_depends = ["test_expected_functions_exist"]

        module_scope['test_docstring_exists'] = pytest_decorate(
            pytest_name, pytest_depends,
            partial(test_docstring_exists_pretest, file_function_map, **test_docstring_exists)
        )


def test_expected_files_exist_pretest(
    file_function_map: dict[str, list[str]]=dict(),
):
    # Check user file names

    wrongly_named_files = find_missing_expected_files(file_function_map.keys())

    from shlomobot_pytest.utils import create_custom_error_json
    custom_error_message = create_custom_error_json(
        feedback=f"The name for the following submitted file(s) are wrong: {', '.join(wrongly_named_files)}",
        points_per_error=100,
        max_points_deducted=100,
        number_of_errors=1,
    )

    assert wrongly_named_files == [], custom_error_message


def test_expected_functions_exist_pretest(
    file_function_map: dict[str, list[str]]=dict(),
):
    # Checks user function names

    wrongly_named_functions = find_missing_expected_functions(file_function_map)
    from shlomobot_pytest.utils import create_custom_error_json

    custom_error_message = create_custom_error_json(
        feedback=f"The name for the following function(s) are wrong: {', '.join(wrongly_named_functions)}",
        points_per_error=100,
        max_points_deducted=100,
        number_of_errors=len(wrongly_named_functions),
    )

    assert wrongly_named_functions == [], custom_error_message


def test_pep8_compliant_pretest(
    file_function_map: dict[str, list[str]]=dict(),
):
    # Checks that pep8 is conformed to

    pep8_errors = pep8_conformance(file_function_map.keys())

    combined_errors_string_list = []
    total_num_of_errors = 0
    for filename, error_messages_list in pep8_errors.items():
        individual_file_errors_string = f"{filename} - {', '.join(error_messages_list)}"
        combined_errors_string_list.append(individual_file_errors_string)
        total_num_of_errors += len(error_messages_list)
    from shlomobot_pytest.utils import create_custom_error_json

    custom_error_message = create_custom_error_json(
        feedback=f"{'; '.join(combined_errors_string_list)}",
        points_per_error=5,
        max_points_deducted=30,
        number_of_errors=total_num_of_errors,
    )

    assert pep8_errors == {}, custom_error_message


def test_contains_main_function_pretest(
    file_function_map: dict[str, list[str]]=dict(),
    feedback: str="Where is your main() function?",
    points_per_error: int=10,
    max_points_deducted: int=10,
    number_of_errors: int=1,
):
    # Check that the code contains the main() function
    from shlomobot_pytest.utils import create_custom_error_json

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in file_function_map.keys():
        assert contains_main_function(filename), custom_error_message


def test_name_eq_main_statement_exist_pretest(
    file_function_map: dict[str, list[str]]=dict(),
    feedback: str="Where is the standard boilerplate to call the main() function?",
    points_per_error: int=10,
    max_points_deducted: int=10,
    number_of_errors: int=1,
):
    # Check that 'if __name__ == "__main__" statement' exists

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in file_function_map.keys():
        assert contains_name_eq_main_statement(filename), custom_error_message


def test_main_function_is_last_function_pretest(
    file_function_map: dict[str, list[str]]=dict(),
    feedback: str="Your main() function should be the last function.",
    points_per_error: int=10,
    max_points_deducted: int=10,
    number_of_errors: int=1,
):
    # Check that main() function is the last function

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in file_function_map.keys():
        assert is_main_function_last(filename), custom_error_message


def test_docstring_exists_pretest(
    file_function_map: dict[str, list[str]]=dict(),
    feedback: str="You are missing docstrings.",
    points_per_error: int=5,
    max_points_deducted: int=5,
    number_of_errors: int=1,
):
    # Check to see if the student have added a docstring for their function

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    functions_with_missing_docstring = find_functions_with_missing_docstrings(file_function_map.keys())

    assert len(functions_with_missing_docstring) == 0, custom_error_message
