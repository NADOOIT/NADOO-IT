import random
import string


def get__new_user_code() -> str:
    user_code = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    )
    return user_code


def check__valid_user_code(user_code: str) -> bool:
    if len(user_code) > 6:
        return False
    if user_code.isalnum():
        return True
    if not user_code[0].isalpha():
        return True

    import re

    if bool(re.search("^[a-zA-Z0-9]*$", user_code)) == True:
        return False
    else:
        return True
    return True
