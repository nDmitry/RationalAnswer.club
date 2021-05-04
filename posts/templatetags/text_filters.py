import json
import math
from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.defaultfilters import date
from django.utils.html import escape
from django.utils.safestring import mark_safe
from typus import ru_typus

from common.regexp import YOUTUBE_RE
from common.markdown.markdown import markdown_text

register = template.Library()


@register.filter(is_safe=True)
def nl_to_p(text):
    if not text:
        return ""
    text = escape(text)
    return mark_safe(text.replace("\n", "</p><p>").replace("\r\n", "</p><p>"))


@register.filter(is_safe=True)
def markdown(text):
    return mark_safe(markdown_text(text))


@register.filter
def ceil(value):
    return math.ceil(value or 0)


@register.filter
def cool_number(value, num_decimals=1):
    """
    11500 -> 11.5K, etc
    """
    int_value = int(value)
    formatted_number = "{{:.{}f}}".format(num_decimals)
    if int_value < 1000:
        return str(int_value)
    elif int_value < 1000000:
        return formatted_number.format(int_value / 1000.0).rstrip("0.") + "K"
    else:
        return formatted_number.format(int_value / 1000000.0).rstrip("0.") + "M"


@register.filter
def cool_date(dt):
    """
    datetime -> "two days ago"
    """
    now = datetime.utcnow()
    if dt > now - timedelta(days=2):
        # recent
        return naturaltime(dt)
    elif dt.year != now.year:
        # different year
        return date(dt, "j E Y")
    else:
        # standard format
        return date(dt, "j E в H:i")


@register.filter
def percentage_of(value, arg):
    if not value:
        return 0

    if not arg:
        return 100

    return int(float(value) / float(arg) * 100)


@register.filter
def rupluralize(value, arg="дурак,дурака,дураков"):
    args = arg.split(",")
    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
        return args[1]
    else:
        return args[2]


@register.filter
def rutypography(value):
    return ru_typus(value)

@register.filter
def uncapitalize(value):
    if value and isinstance(value, str) and value[0].isupper():
        return value[0].lower() + value[1:]
    return value


@register.filter
def is_video(value):
    extension = value[value.rfind(".") + 1:].lower()
    return extension in settings.VIDEO_EXTENSIONS


@register.filter
def resized_image(value, arg="full"):
    if not value or "://i.rationalanswer.ru/" not in value:
        return value

    if is_video(value):
        return value

    if value.startswith("https://i.rationalanswer.ru/full/"):
        return value.replace(
            "https://i.rationalanswer.ru/full/", "https://i.rationalanswer.ru/{}/".format(arg)
        )
    else:
        return value


@register.filter
def youtube_id(value):
    youtube_match = YOUTUBE_RE.match(value)
    if youtube_match:
        return youtube_match.group(1)
    return ""


@register.filter()
def jsonify(value):
    return json.dumps(value)
