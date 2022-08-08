from shlomobot_pytest.utils import create_custom_error_json


def missing_files_error_message(
    wrongly_named_files: list[str],
    points_per_error: int = 100,
    max_points_deducted: int = 100,
):
    """Create a custom error message that is default for case of missing expected files"""

    # Default feedback for missing expected files
    feedback = f"The name for the following submitted file(s) are wrong: {', '.join(wrongly_named_files)}"
    number_of_errors = len(wrongly_named_files)

    custom_error_message = create_custom_error_json(
        feedback,
        points_per_error,
        max_points_deducted,
        number_of_errors,
    )
    return custom_error_message


def missing_functions_error_message(
    wrongly_named_functions: list[str],
    points_per_error: int = 100,
    max_points_deducted: int = 100,
):
    """Create a custom error message that is default for case of missing expected functions"""

    # Default feedback for missing expected functions
    feedback = f"The name for the following function(s) are wrong: {', '.join(wrongly_named_functions)}"
    number_of_errors = len(wrongly_named_functions)

    custom_error_message = create_custom_error_json(
        feedback,
        points_per_error,
        max_points_deducted,
        number_of_errors,
    )
    return custom_error_message


def pep8_conformance_error_message(
    pep8_errors: dict[str, list[str]],
    points_per_error: int = 5,
    max_points_deducted: int = 30,
):
    """Create a custom error message that is default for case of errors in Pep8 conformance"""

    combined_errors_string_list = []
    total_num_of_errors = 0
    for filename, error_messages_list in pep8_errors.items():
        individual_file_errors_string = f"{filename} - {', '.join(error_messages_list)}"
        combined_errors_string_list.append(individual_file_errors_string)
        total_num_of_errors += len(error_messages_list)

    # Default feedback for Pep8 errors
    feedback = f"{'; '.join(combined_errors_string_list)}"

    custom_error_message = create_custom_error_json(
        feedback, points_per_error, max_points_deducted, total_num_of_errors
    )
    return custom_error_message
