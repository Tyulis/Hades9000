from django import template
from main.models import *

register = template.Library()

@register.filter(name='dictget')
def dictget(dic, key):
	return dic[key]

@register.filter(name='times')
def times(upper):
	return range(upper)

@register.filter(name='add')
def add(a, b):
	return a + b

@register.filter(name='modulo')
def modulo(a, b):
	return a % b

@register.filter(name='round')
def round_tag(a):
	return round(a)
