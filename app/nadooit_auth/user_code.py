# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Compatibility: Django 4
# License: TBD

import random
import string


def get__new_user_code() -> str:

    """

    Generates a new user code.

    """

    user_code = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    )
    return user_code


def check__valid_user_code(user_code: str) -> bool:

    """

    Checks if a user code is valid.

    """
    # Valid if exactly 6 ASCII alphanumeric characters.
    if not isinstance(user_code, str):
        return False
    if len(user_code) != 6:
        return False
    return user_code.isalnum()
