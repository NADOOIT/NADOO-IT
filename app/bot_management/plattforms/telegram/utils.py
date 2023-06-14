from bot_management.models import BotPlatform
from functools import wraps

bot_routes = {}


def register_bot_route(secret_url):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = BotPlatform.objects.get(secret_url=secret_url).access_token
            kwargs["token"] = token
            return view_func(request, *args, **kwargs)

        bot_routes[secret_url] = _wrapped_view
        return _wrapped_view

    return decorator
