import pytz
import datetime
from django import template
from main.models import *

register = template.Library()

@register.filter(name='localize')
def localize(dt, offset):
    return dt + offset

@register.filter(name='asdate')
def asdate(dt):
    return dt.date()

@register.filter(name='dateformat')
def dateformat(dt):
    return dt.strftime('%A %d %B')

@register.filter(name='updatefmt')
def updatefmt(dt):
    return dt.strftime('%d%m%Y-%H%M')

@register.filter(name='formdate')
def formdate(dt):
    return dt.strftime('%Y-%m-%d')

@register.filter(name='formtime')
def formtime(dt):
    return dt.strftime('%H:%M')
