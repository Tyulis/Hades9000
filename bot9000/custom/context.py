# -*- coding:utf-8 -*-

import lupa
from main.models import *
from .api import *


class CustomCommandContext (object):
	def __init__(self, message, arguments, group, player, bot):
		self.message = message
		self.channel = message.channel
		self.guild = message.guild
		self.author = message.author
		self.arguments = arguments
		self.group = group
		self.player = player
		self.bot = bot
