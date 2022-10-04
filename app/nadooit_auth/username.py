import random
import string


def get__new_username() -> str:
    username = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(20)
    )
    return username
