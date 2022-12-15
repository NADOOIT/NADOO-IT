# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Compatibility: Django 4
# License: TBD

import random
import string


def get__new_username() -> str:

    """

    This function generates a new username for a new user.

    """

    username = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(20)
    )
    return username
