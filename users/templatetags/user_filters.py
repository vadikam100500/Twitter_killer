from django import template
from twitter_killer.settings import MEDIA_URL

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.simple_tag
def media_url():
    return MEDIA_URL
