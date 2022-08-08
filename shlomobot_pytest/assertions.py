from shlomobot_pytest.pretest import (
    find_missing_expected_files,
    find_missing_expected_functions,
    pep8_conformance,
)

from shlomobot_pytest.utils import create_custom_error_json


def assert_missing_expected_files(filenames_list: list[str]):
    """Assert that no expected files are missing; If missing, raise a custom error message"""

    wrongly_named_files = find_missing_expected_files(filenames_list)

    custom_error_message = create_custom_error_json(
        feedback=f"The name for the following submitted file(s) are wrong: {', '.join(wrongly_named_files)}",
        points_per_error=100,
        max_points_deducted=100,
        number_of_errors=len(wrongly_named_files),
    )

    assert wrongly_named_files == [], custom_error_message


def assert_missing_expected_functions(file_function_map: dict[str, list[str]]):
    """Assert that no expected functions are missing; If missing, raise a custom error message"""

    wrongly_named_functions = find_missing_expected_functions(file_function_map)

    custom_error_message = create_custom_error_json(
        feedback=f"The name for the following function(s) are wrong: {', '.join(wrongly_named_functions)}",
        points_per_error=100,
        max_points_deducted=100,
        number_of_errors=len(wrongly_named_functions),
    )

    assert wrongly_named_functions == [], custom_error_message


def assert_pep8_conformance(filenames_list: list[str]):
    """Assert that Pep8 is conformed to; If not, raise a custom error message with the errors"""
    pep8_errors = pep8_conformance(filenames_list)

    combined_errors_string_list = []
    total_num_of_errors = 0
    for filename, error_messages_list in pep8_errors.items():
        individual_file_errors_string = f"{filename} - {', '.join(error_messages_list)}"
        combined_errors_string_list.append(individual_file_errors_string)
        total_num_of_errors += len(error_messages_list)

    custom_error_message = create_custom_error_json(
        total_num_of_errors,
        feedback=f"{'; '.join(combined_errors_string_list)}",
        points_per_error=5,
        max_points_deducted=30,
    )

    assert pep8_errors == {}, custom_error_message
