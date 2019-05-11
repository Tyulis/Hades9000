# -*- coding:utf-8 -*-

import asyncio
import discord
import lupa
from main.models import *


class CustomCommandCapsule (object):
	def asyncrun(self, coroutine):
		if self.context.bot.loop is not None:
			return self.context.bot.loop.call_soon(asyncio.ensure_future, coroutine)
		else:
			return asyncio.get_event_loop().call_soon(asyncio.ensure_future, coroutine)

	def string(self, identifier, language):
		if language in self.strings:
			if identifier in self.strings[language]:
				return self.strings[language][identifier]
		if self.defaultlang in self.strings:
			if identifier in self.strings[self.defaultlang]:
				return self.strings[self.defaultlang][identifier]
		return 'Bad string identifier : %s' % identifier

	strings = {
		'FR': {
		}
	}

class ContextCapsule (CustomCommandCapsule):
	def __init__(self, context):
		self.context = context

	def message(self):
		return MessageCapsule(self.context.message, self.context)

	def channel(self):
		return ChannelCapsule(self.context.channel, self.context)

	def guild(self):
		return GuildCapsule(self.context.guild, self.context)

	def author(self):
		return MemberCapsule(self.context.message.author, self.context)

	def player(self):
		return PlayerCapsule(self.context.player, self.context)

	def corporation(self):
		if player.discordid is not None:
			return CorporationCapsule(self.context.player.corp, self.context)
		else:
			return None

	def get_role(self, name):
		role = discord.utils.get(self.context.guild.roles, name=name)
		if role is not None:
			return RoleCapsule(role, self.context)
		else:
			return None

	def get_role_byid(self, id):
		role = discord.utils.get(self.context.guild.roles, id=id)
		if role is not None:
			return RoleCapsule(role, self.context)
		else:
			return None

	def answer(self, content):
		"""#ContextCapsule.answer(content)
		Sends a message to the channel where the command has been sent. Shortcut for context.channel().send(content)
		- **content** : The content of the message to send
		- **Returns** : The sent message"""
		self.asyncrun(self.context.channel.send(content))

class CorpGroupCapsule (CustomCommandCapsule):
	def __init__(self, group, context):
		self.group = group
		self.context = context

	def corporations(self):
		"""#CorpGroupCapsule.corporations()
		- **Returns** : A list of all the corporation in the group as `CorporationCapsule` objects"""
		return [CorporationCapsule(corp, self.context) for corp in self.group.corporations()]

	def name(self):
		"""#CorpGroupCapsule.name()
		- **Returns** : The name of the group"""
		return self.group.name

	def publiclink(self):
		"""#CorpGroupCapsule.publiclink()
		- **Returns** : Wether the discord invite link of the group is public"""
		return self.group.publiclink

	def publicmembers(self):
		"""#CorpGroupCapsule.publicmembers()
		- **Returns** : Wether the members list of the group is public"""
		return self.group.publicmembers

	def publicws(self):
		"""#CorpGroupCapsule.publicws()
		- **Returns** : Wether the white stars of the group are public"""
		return self.group.publicws

	def notifications_enabled(self):
		"""#CorpGroupCapsule.notifications_enabled()
		- **Returns** : Wether the status notifications are enabled for the group's discord
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return self.group.notifications
		else:
			raise AttributeError('CorpGroup.notifications_enabled() : access denied')

	def notifications_channel(self):
		"""#CorpGroupCapsule.notifications_channel()
		- **Returns** : The channel where the status, welcome and leave notifications are sent on the group's discord as a `ChannelCapsule` object
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return ChannelCapsule(discord.utils.get(self.context.guild.channels, id=self.group.notifchannel), self.context)
		else:
			raise AttributeError('CorpGroup.notifications_channel() : access denied')

	def management_channel(self):
		"""#CorpGroupCapsule.notifications_channel()
		- **Returns** : The channel where the responsible-only notifications are sent on the group's discord as a `ChannelCapsule` object
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return ChannelCapsule(discord.utils.get(self.context.guild.channel, id=self.group.managementchannel), self.context)
		else:
			raise AttributeError('CorpGroup.management_channel() : access denied')

	def language(self):
		"""#CorpGroupCapsule.language()
		- **Returns** : The language of the group, as a 2-characters code ("EN", "FR", "DE", ...)
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return self.group.language
		else:
			raise AttributeError('CorpGroup.language() : access denied')

	def admin_role(self):
		"""#CorpGroupCapsule.admin_role()
		- **Returns** : The admin role of the group's server as a `RoleCapsule`
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return RoleCapsule(discord.utils.get(self.context.guild.roles, id=self.group.adminrole))
		else:
			raise AttributeError('CorpGroup.admin_role() : access denied')

	def responsible_role(self):
		"""#CorpGroupCapsule.responsible_role()
		- **Returns** : The responsible role of the group's server as a `RoleCapsule`
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return RoleCapsule(discord.utils.get(self.context.guild.roles, id=self.group.resporole))
		else:
			raise AttributeError('CorpGroup.responsible_role() : access denied')

	def moderator_role(self):
		"""#CorpGroupCapsule.moderator_role()
		- **Returns** : The moderator role of the group's server as a `RoleCapsule`
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return RoleCapsule(discord.utils.get(self.context.guild.roles, id=self.group.modorole))
		else:
			raise AttributeError('CorpGroup.moderator_role() : access denied')

	def member_role(self):
		"""#CorpGroupCapsule.member_role()
		- **Returns** : The member role of the group's server as a `RoleCapsule`
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return RoleCapsule(discord.utils.get(self.context.guild.roles, id=self.group.memberrole))
		else:
			raise AttributeError('CorpGroup.member_role() : access denied')

	def welcome_enabled(self):
		"""#CorpGroupCapsule.welcome_enabled()
		- **Returns** : Wether the welcome notifications are enabled for the group's server
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return self.group.enable_welcome
		else:
			raise AttributeError('CorpGroup.welcome_enabled() : access denied')

	def leavenotif_enabled(self):
		"""#CorpGroupCapsule.leavenotif_enabled()
		- **Returns** : Wether the leave notifications are enabled for the group's server
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			return self.group.enable_welcome
		else:
			raise AttributeError('CorpGroup.leavenotif_enabled() : access denied')

	def switch_welcome(self, enabled=None):
		"""#CorpGroupCapsule.switch_welcome(enabled=None)
		- **enabled** : If the welcome notifications must be enabled or disabled. If not specified, toggle them.
		- **Returns** : The new welcome notifications enabling state
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			if enabled is None:
				self.group.enable_welcome = not self.group.enable_welcome
			else:
				self.group.enable_welcome = enabled
			self.group.save()
			return self.group.enable_welcome
		else:
			raise AttributeError('CorpGroup.switch_welcome() : access denied')

	def switch_leavenotif(self, enabled=None):
		"""#CorpGroupCapsule.switch_leavenotif(enabled=None)
		- **enabled** : If the leave notifications must be enabled or disabled. If not specified, toggle them.
		- **Returns** : The new leave notifications enabling state
		- **Errors** : Can't access to the others groups data"""
		if self.group == self.context.group:
			if enabled is None:
				self.group.enable_leavenotif = not self.group.enable_leavenotif
			else:
				self.group.enable_leavenotif = enabled
		else:
			raise AttributeError('CorpGroup.switch_welcome() : access denied')

	def isgroup(self):
		"""#CorpGroupCapsule.isgroup()
		- **Returns** : Wether it is an actual group or a single corporation"""
		return self.group.isgroup

class CorporationCapsule (CustomCommandCapsule):
	def __init__(self, corp, context):
		self.corp = corp
		self.context = context

	def name(self):
		return self.corp.name

	def publiclink(self):
		return self.corp.group.publiclink

	def publicmembers(self):
		return self.corp.group.publicmembers

	def publicws(self):
		return self.corp.group.publicws

	def group(self):
		return CorpGroupCapsule(self.corp.group)

class PlayerCapsule (CustomCommandCapsule):
	def __init__(self, player, context):
		self.player = player
		self.context = context

class WSCapsule (CustomCommandCapsule):
	def __init__(self, ws, context):
		self.ws = ws
		self.context = context

class WSPlayerCapsule (CustomCommandCapsule):
	def __init__(self, wsplayer, context):
		self.wsplayer = wsplayer
		self.context = context

class RSCapsule (CustomCommandCapsule):
	def __init__(self, rs, context):
		self.rs = rs
		self.context = context

class GuildCapsule (CustomCommandCapsule):
	def __init__(self, guild, context):
		self.guild = guild
		self.context = context

class ChannelCapsule (CustomCommandCapsule):
	def __init__(self, channel, context):
		self.channel = channel
		self.context = context

	def send(self, content):
		return self.asyncrun(self.channel.send(content))

class MessageCapsule (CustomCommandCapsule):
	def __init__(self, message, context):
		self.message = message
		self.context = context

	def delete(self):
		self.asyncrun(self.message.delete())

	def edit(self, content):
		self.message = self.asyncrun(self.message.edit(content=content))

class MemberCapsule (CustomCommandCapsule):
	def __init__(self, member, context):
		self.member = member
		self.context = context

	def add_role(self, rolecaps):
		self.asyncrun(self.member.add_roles(rolecaps.role))

	def remove_role(self, rolecaps):
		self.asyncrun(self.member.remove_roles(rolecaps.role))

class RoleCapsule (CustomCommandCapsule):
	def __init__(self, role, context):
		self.role = role
		self.context = context

	def color(self):
		return self.role.colour
	def colour(self):
		return self.role.colour

	def rename(self, name):
		self.asyncrun(self.role.edit(name=name))

	def set_color(self, value):
		color = discord.Colour(value)
		print(color)
		self.asyncrun(self.role.edit(colour=color))
