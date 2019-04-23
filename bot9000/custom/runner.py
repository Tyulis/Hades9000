# -*- coding:utf-8 -*-


import lupa
from main.models import *
from bot9000.commands.base import Bot9000Command
from .context import CustomCommandContext
from .api import *


class CustomCommandRunner (Bot9000Command):
	def __init__(self, name, minimum_role, arguments, code, group):
		self.lua = lupa.LuaRuntime(unpack_returned_tuples=True, attribute_filter=self.filter_attribute_access)
		self.name = name
		self.group = group
		self.minimum_role = minimum_role
		self.arguments = arguments
		self.parser = self.make_parser(self.arguments)
		self.function = self.lua.eval(code)

	async def run(self, message, arguments, group, player, bot):
		context = CustomCommandContext(message, arguments, group, player, bot)
		contextcaps = ContextCapsule(context)
		self.function(contextcaps)

	def filter_attribute_access(self, obj, attr, is_setting):
		if isinstance(attr, str):
			if not attr.startswith('_'):
				return attr
		raise AttributeError('Access denied')
