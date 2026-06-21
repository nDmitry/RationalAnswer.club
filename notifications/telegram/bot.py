import logging

import telegram
from django.conf import settings

log = logging.getLogger()

_request_kwargs = None
if settings.TELEGRAM_PROXY_URL:
    _request_kwargs = {"proxy_url": settings.TELEGRAM_PROXY_URL}
bot = (
    telegram.Bot(token=settings.TELEGRAM_TOKEN, request_kwargs=_request_kwargs)
    if settings.TELEGRAM_TOKEN
    else None
)
