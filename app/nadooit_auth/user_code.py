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
    # A user code is valid if it is a string of 6 characters.
    if len(user_code) > 6:
        return False
    if len(user_code) < 6:
        return False

    # A user code is valid if it contains only letters and digits.
    if user_code.isalnum():
        return True

    # A user code is invalid if it contains other characters.
    if user_code.isalpha():
        return True

    import re

    # A user code is valid if it contains only letters and digits.
    if bool(re.search("^[a-zA-Z0-9]*$", user_code)) == True:
        return False
    else:
        return True
