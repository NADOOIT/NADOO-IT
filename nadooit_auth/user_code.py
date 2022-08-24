import random
import string


def get__new_user_code() -> str:
    user_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    return user_code