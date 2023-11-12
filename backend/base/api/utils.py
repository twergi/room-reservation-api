from typing import TYPE_CHECKING, Optional
from rest_framework.exceptions import ValidationError
from django.conf import settings
from datetime import datetime as dt_datetime


if TYPE_CHECKING:
    from django.http import HttpRequest
    from datetime import date as dt_date, datetime as dt_datetime


def validate_queryparam_date(request: "HttpRequest", field: str) -> Optional["dt_date"]:
    date_str: str = request.query_params.get(field)

    if date_str is None:
        return None

    try:
        date = dt_datetime.strptime(date_str, settings.DATE_FORMAT).date()
    except ValueError as exc:
        raise ValidationError({field: exc})

    return date
