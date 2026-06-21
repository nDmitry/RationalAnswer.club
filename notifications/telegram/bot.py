import logging

import telegram
from django.conf import settings
from telegram.utils.request import Request

log = logging.getLogger()

_request = None
if settings.TELEGRAM_PROXY_URL:
    _request = Request(proxy_url=settings.TELEGRAM_PROXY_URL)
bot = (
    telegram.Bot(token=settings.TELEGRAM_TOKEN, request=_request)
    if settings.TELEGRAM_TOKEN
    else None
)
