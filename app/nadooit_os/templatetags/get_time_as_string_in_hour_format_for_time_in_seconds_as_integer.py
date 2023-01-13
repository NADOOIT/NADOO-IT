from django import template

register = template.Library()
from nadooit_time_account.models import (
    get_time_as_string_in_hour_format_for_time_in_seconds_as_integer,
)


def templatetag_get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(
    time_in_seconds_as_integer,
):
    if time_in_seconds_as_integer is None:
        return "-"
    else:
        return get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(
            time_in_seconds_as_integer
        )


register.filter(
    "get_time_as_string_in_hour_format_for_time_in_seconds_as_integer",
    templatetag_get_time_as_string_in_hour_format_for_time_in_seconds_as_integer,
)
