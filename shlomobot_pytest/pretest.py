"""This module contains test functions that are primarily needed for all test files"""
import pytest

from shlomobot_pytest.utils import create_custom_error_json
from functools import partial

from shlomobot_pytest.common_tests import (
    find_missing_expected_files,
    find_missing_expected_functions,
    pep8_conformance,
    contains_main_function,
    contains_name_eq_main_statement,
    is_main_function_last,
    find_functions_with_missing_docstrings,
)

def register_tests(
    file_function_map,
    test_expected_files_exist=None,
    test_expected_functions_exist=None,
    test_pep8_compliant=None,
    test_contains_main_function=None,
    test_name_eq_main_statement_exist=None,
    test_main_function_is_last_function=None,
    test_docstring_exists=None,
):
    """
    Sample to call the function:
    register_tests(
        FILE_FUNCTION_MAP,
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
    """
    if test_expected_files_exist is not None:
        global test_expected_files_exist_pretest
        test_expected_files_exist_pretest = partial(default_test_expected_files_exist, file_function_map, **test_expected_files_exist)

    if test_expected_functions_exist is not None:
        global test_expected_functions_exist_pretest
        test_expected_functions_exist_pretest = partial(default_test_expected_functions_exist, file_function_map, **test_expected_functions_exist)

    if test_pep8_compliant is not None:
        global test_pep8_compliant_pretest
        test_pep8_compliant_pretest = partial(default_test_pep8_compliant, file_function_map, **test_pep8_compliant)

    if test_contains_main_function is not None:
        global test_contains_main_function_pretest
        test_contains_main_function_pretest = partial(default_test_contains_main_function, file_function_map, **test_contains_main_function)

    if test_name_eq_main_statement_exist is not None:
        global test_name_eq_main_statement_exist_pretest
        test_name_eq_main_statement_exist_pretest = partial(default_test_name_eq_main_statement_exist, file_function_map, **test_name_eq_main_statement_exist)

    if test_main_function_is_last_function is not None:
        global test_main_function_is_last_function_pretest
        test_main_function_is_last_function_pretest = partial(default_test_main_function_is_last_function, file_function_map, **test_main_function_is_last_function)

    if test_docstring_exists is not None:
        global test_docstring_exists_pretest
        test_docstring_exists_pretest = partial(default_test_docstring_exists, file_function_map, **test_docstring_exists)


@pytest.mark.skip("Not Required")
def test_expected_files_exist_pretest():
    return

@pytest.mark.skip("Not Required")
def test_expected_functions_exist_pretest():
    return

@pytest.mark.skip("Not Required")
def test_pep8_compliant_pretest():
    return

@pytest.mark.skip("Not Required")
def test_contains_main_function_pretest():
    return

@pytest.mark.skip("Not Required")
def test_name_eq_main_statement_exist_pretest():
    return

@pytest.mark.skip("Not Required")
def test_main_function_is_last_function_pretest():
    return

@pytest.mark.skip("Not Required")
def test_docstring_exists_pretest():
    return


def default_test_expected_files_exist(
    FILE_FUNCTION_MAP=dict(),
):
    # Check user file names

    wrongly_named_files = find_missing_expected_files(FILE_FUNCTION_MAP.keys())

    custom_error_message = create_custom_error_json(
        feedback=f"The name for the following submitted file(s) are wrong: {', '.join(wrongly_named_files)}",
        points_per_error=100,
        max_points_deducted=100,
        number_of_errors=1,
    )

    assert wrongly_named_files == [], custom_error_message


def default_test_expected_functions_exist(
    FILE_FUNCTION_MAP=dict(),
):
    # Checks user function names

    wrongly_named_functions = find_missing_expected_functions(FILE_FUNCTION_MAP)

    custom_error_message = create_custom_error_json(
        feedback=f"The name for the following function(s) are wrong: {', '.join(wrongly_named_functions)}",
        points_per_error=100,
        max_points_deducted=100,
        number_of_errors=len(wrongly_named_functions),
    )

    assert wrongly_named_functions == [], custom_error_message


def default_test_pep8_compliant(
    FILE_FUNCTION_MAP=dict(),
):
    # Checks that pep8 is conformed to

    pep8_errors = pep8_conformance(FILE_FUNCTION_MAP.keys())

    combined_errors_string_list = []
    total_num_of_errors = 0
    for filename, error_messages_list in pep8_errors.items():
        individual_file_errors_string = f"{filename} - {', '.join(error_messages_list)}"
        combined_errors_string_list.append(individual_file_errors_string)
        total_num_of_errors += len(error_messages_list)

    custom_error_message = create_custom_error_json(
        feedback=f"{'; '.join(combined_errors_string_list)}",
        points_per_error=5,
        max_points_deducted=30,
        number_of_errors=total_num_of_errors,
    )

    assert pep8_errors == {}, custom_error_message


def default_test_contains_main_function(
    FILE_FUNCTION_MAP=dict(),
    feedback="Where is your main() function?",
    points_per_error=10,
    max_points_deducted=10,
    number_of_errors=1,
):
    # Check that the code contains the main() function

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in FILE_FUNCTION_MAP.keys():
        assert contains_main_function(filename), custom_error_message


def default_test_name_eq_main_statement_exist(
    FILE_FUNCTION_MAP=dict(),
    feedback="Where is the standard boilerplate to call the main() function?",
    points_per_error=10,
    max_points_deducted=10,
    number_of_errors=1,
):
    # Check that 'if __name__ == "__main__" statement' exists

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in FILE_FUNCTION_MAP.keys():
        assert contains_name_eq_main_statement(filename), custom_error_message


def default_test_main_function_is_last_function(
    FILE_FUNCTION_MAP=dict(),
    feedback="Your main() function should be the last function.",
    points_per_error=10,
    max_points_deducted=10,
    number_of_errors=1,
):
    # Check that main() function is the last function

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    for filename in FILE_FUNCTION_MAP.keys():
        assert is_main_function_last(filename), custom_error_message


def default_test_docstring_exists(
    FILE_FUNCTION_MAP=dict(),
    feedback="You are missing docstrings.",
    points_per_error=5,
    max_points_deducted=5,
    number_of_errors=1,
):
    # Check to see if the student have added a docstring for their function

    custom_error_message = create_custom_error_json(
        feedback=feedback,
        points_per_error=points_per_error,
        max_points_deducted=max_points_deducted,
        number_of_errors=number_of_errors,
    )

    functions_with_missing_docstring = find_functions_with_missing_docstrings(FILE_FUNCTION_MAP.keys())

    assert len(functions_with_missing_docstring) == 0, custom_error_message
