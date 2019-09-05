# -*- coding:utf-8 -*-

import shlex
import argparse
import secrets
import discord
from main.models import *
from django.core.exceptions import ObjectDoesNotExist

from .commands import COMMANDS
from .commands.base import ArgumentError
from .custom.runner import CustomCommandRunner

SITE_URL = 'http://localhost:8000/'
roles_ids = ('anyone', 'member', 'moderator', 'responsible', 'admin')

class dummygp:
    language = 'FR'
    discordid = None

class Hades9000Bot (discord.Client):
    defaultlang = 'FR'

    async def on_ready(self):
        print('Ready, initializing...')
        self.customcmds = {}
        for group in CorpGroup.objects.all():
            print('Setting up group %s' % group.name)
            await self.setup_group(group)
        print('Let\'s go !')

    async def setup_group(self, group):
        cmds = group.getcustomcommands()
        for cmdname, cmd in cmds.items():
            print(cmd)
            cmd['runner'] = CustomCommandRunner(cmdname, cmd['minimum_role'], cmd['arguments'], cmd['code'], group)
        self.customcmds[group.id] = cmds
        guild = discord.utils.get(self.guilds, id=group.discordid)
        for player in group.members():
            discorduser = discord.utils.get(guild.members, id=player.discordid)
            roleids = [role.id for role in discorduser.roles]
            player.admin = group.adminrole in roleids
            player.responsible = group.resporole in roleids
            player.moderator = group.modorole in roleids
            if group.memberrole not in roleids:
                player.corp = None
            player.save()
        #if group.notifications:
        #    await self.send_notification(group, self.string('online_notification', group.language))

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.strip().startswith('$'):
            try: group = CorpGroup.objects.get(discordid=message.guild.id)
            except ObjectDoesNotExist: group = dummygp
            try: player = Player.objects.get(discordid=message.author.id)
            except ObjectDoesNotExist:
                player = dummygp
                player.language = group.language
            await self.run_command(message, group, player)

    async def on_message_edit(self, before, after):
        if after.author == self.user:
            return
        if after.content.strip().startswith('$') and before.content != after.content:
            try: group = CorpGroup.objects.get(discordid=after.guild.id)
            except ObjectDoesNotExist: group = dummygp
            try: player = Player.objects.get(discordid=after.author.id)
            except ObjectDoesNotExist:
                player = dummygp
                player.language = group.language
            await self.run_command(after, group, player)

    async def on_member_join(self, member):
        try:
            group = CorpGroup.objects.get(discordid=member.guild.id)
        except ObjectDoesNotExist:
            return
        if group.enable_welcome:
            if group.private_welcome:
                await member.send(group.welcome)
            else:
                await self.send_notification(group, group.welcome)

    async def on_member_remove(self, member):
        try:
            group = CorpGroup.objects.get(discordid=member.guild.id)
        except ObjectDoesNotExist:
            return
        if group.enable_leavenotif:
            print(member.guild)
            await self.send_notification(group, self.string('leave_notif', group.language) % member.name)

    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return
        try: group = CorpGroup.objects.get(discordid=after.guild.id)
        except ObjectDoesNotExist: return
        try: player = Player.objects.get(discordid=after.id)
        except ObjectDoesNotExist: return
        print("Update of %s" % player.name)
        roleids = [role.id for role in after.roles]
        player.admin = group.adminrole in roleids
        player.responsible = group.resporole in roleids
        player.moderator = group.modorole in roleids
        if group.memberrole not in roleids:
            player.corp = None
        player.save()

    async def run_command(self, message, group, player):
        discorduser = message.author
        content = message.content.strip(' \t\n$!')
        commandname = content.split()[0].strip()

        command = self.get_command(commandname, group)
        if isinstance(command, str):
            if command == 'unknown':
                await message.channel.send(self.string('bad_command', player.language) % commandname)
                return
            elif command.startswith('inactive'):
                module = command.split()[1]
                await message.channel.send(self.string('inactive_command', player.language) % (commandname, module, module))
                return
        if command.minimum_role != 'anyone' and not (group.discordid is None and command.name in ('setupgroup', 'setupcorp')):
            minrole = self.get_role(command.minimum_role, group, message.guild)
            if discorduser.top_role < minrole:
                await message.channel.send(self.string('permission_denied', player.language) % minrole.name)
                return

        if command.parser is None:
            command.parser = command.make_parser(command.arguments)
        parser = command.parser
        try:
            arguments = parser.parse_args(shlex.split(message.content.partition(' ')[2]))
            print(commandname, arguments)
            await command.run(message, arguments, group, player, self)
        except ArgumentError:
            await message.channel.send(self.string('bad_arguments', player.language) % commandname)
            await message.channel.send(command.help(player.language))

    async def send_split(self, channel, content):
        split = ''
        for line in content.splitlines():
            if len(split) + len(line) < 2000:
                split += line + '\n'
            else:
                await channel.send(split)
                split = line + '\n'
        if split != '':
            await channel.send(split)

    def get_command(self, commandname, group):
        if group.discordid is None:
            groupmodules = ('account', 'help')
        else:
            groupmodules = group.getcommandmods()
        for module in COMMANDS:
            if module in groupmodules:
                if commandname in COMMANDS[module]:
                    return COMMANDS[module][commandname]
            elif commandname in COMMANDS[module]:
                return 'inactive ' + module
        if commandname in self.customcmds[group.id]:
            return self.customcmds[group.id][commandname]['runner']
        return 'unknown'

    def all_commands(self, group):
        if group.discordid is None:
            groupmodules = ('account', 'help')
        else:
            groupmodules = group.getcommandmods()
        commands = []
        for module in COMMANDS:
            if module in groupmodules:
                commands.extend([COMMANDS[module][command] for command in COMMANDS[module] if not command.startswith('__')])
        return commands

    def command_modules(self):
        return COMMANDS

    async def send_notification(self, group, message):
        guild = discord.utils.get(self.guilds, id=group.discordid)
        channel = discord.utils.get(guild.channels, id=group.notifchannel)
        if channel is not None:
            await channel.send(message)
        else:
            await guild.send(message)
            await self.send_management_message(group, self.string('bad_notif_channel_error', group.language) % group.notifchannel)

    async def send_management_message(self, group, message):
        guild = discord.utils.get(self.guilds, id=group.discordid)
        channel = discord.utils.get(guild.channels, id=group.managementchannel)
        if channel is not None:
            await channel.send(message)
        else:
            await guild.send(message)
            await self.send_group_admin_message(group, self.string('bad_management_channel_error', group.language) % group.managementchannel)

    async def send_group_admin_message(self, group, message):
        for admin in group.admins():
            if admin.confirmed:
                await admin.send(message)

    async def send_group_message(self, group, message):
        guild = discord.utils.get(self.guilds, id=group.discordid)
        if guild is not None:
            await guild.send(message)
        else:
            await self.send_group_admin_message(group, self.string('bad_guild', group.language) % group.discordid)

    def get_member(self, name, guild):
        user = discord.utils.get(guild.members, nick=name)
        if user is not None:
            return user
        user = discord.utils.get(guild.members, name=name)
        if user is not None:
            return user
        user = discord.utils.get(guild.members, mention=name)
        if user is not None:
            return user
        user = discord.utils.get(guild.members, id=name)
        return user

    def get_role(self, grade, group, guild):
        if grade == 'member':
            return discord.utils.get(guild.roles, id=group.memberrole)
        elif grade == 'moderator':
            return discord.utils.get(guild.roles, id=group.modorole)
        elif grade == 'responsible':
            return discord.utils.get(guild.roles, id=group.resporole)
        elif grade == 'admin':
            return discord.utils.get(guild.roles, id=group.adminrole)
        elif grade == 'rs1':
            return discord.utils.get(guild.roles, id=group.rs1role)
        elif grade == 'rs2':
            return discord.utils.get(guild.roles, id=group.rs2role)
        elif grade == 'rs3':
            return discord.utils.get(guild.roles, id=group.rs3role)
        elif grade == 'rs4':
            return discord.utils.get(guild.roles, id=group.rs4role)
        elif grade == 'rs5':
            return discord.utils.get(guild.roles, id=group.rs5role)
        elif grade == 'rs6':
            return discord.utils.get(guild.roles, id=group.rs6role)
        elif grade == 'rs7':
            return discord.utils.get(guild.roles, id=group.rs7role)
        elif grade == 'rs8':
            return discord.utils.get(guild.roles, id=group.rs8role)
        elif grade == 'rs9':
            return discord.utils.get(guild.roles, id=group.rs9role)
        elif grade == 'rs10':
            return discord.utils.get(guild.roles, id=group.rs10role)


    def get_loop(self):
        if self.loop is not None:
            return self.loop
        else:
            return asyncio.get_event_loop()

    def make_url(self, end):
        return SITE_URL + end

    def generate_temp_password(self):
        return secrets.token_urlsafe(14)

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
            'user_confirm': 'Bonjour, je suis Hades9000. Vous devez confirmer que vous êtes bien %s. Si vous confirmez que vous êtes bien %s, entrez "$y". Si vous n\'êtes pas %s ou que vous ne savez pas pourquoi vous recevez ceci, vous pouvez ignorer ce message.\n*If you are not %s or if you don\'t know why you received this, you can just ignore this message*',
            'corp_confirm': 'Bonjour. Vous devez confirmer que ceci est bien le serveur Discord de la corporation %s. Si vous confirmez que c\'est le cas, entrez "$y". Si ce n\'est pas le discord de %s ou si vous ne savez pas pourquoi vous recevez ceci, vous pouvez ignorer ce message.\n*If this is not the %s\'s discord server or if you don\'t know why you received this, you can just ignore this message*',
            'group_confirm': 'Bonjour. Vous devez confirmer la création du groupe %s, et que ceci est son serveur discord. Si vous confirmez que c\'est le cas, entrez "$y". Si ce n\'est pas le discord de %s ou si vous ne savez pas pourquoi vous recevez ceci, vous pouvez ignorer ce message.\n*If this is not the %s\'s discord server, or if you don\'t know why you received this, you can just ignore this message*',
            'join_group_confirm': 'Bonjour. La corporation %s cherche à rejoindre le groupe %s. Si vous acceptez que cette corporation rejoigne le groupe, entrez "$y". Dans le cas contraire, ou si vous ne savez pas pourquoi vous recevez ce message, entrez "$n".\n*If you don\'t accept this corp or if you don\'t know why you received this, then type "$n".',
            'join_corp_confirm': 'Bonjour. L\'utilisateur %s cherche à rejoindre la corporation %s. Si vous l\'acceptez, entrez "$y". Dans le cas contraire, ou si vous ne savez pas pourquoi vous recevez ceci, entrez "$n".\n*If you don\'t accept %s or if you don\'t know why you received this, type "$n".',

            'online_notification': 'Bonjour. Je suis en ligne.',
            'offline_motification': 'Passage hors-ligne. Au revoir.',
            'leave_notif': '__**%s a quitté le serveur. Bye ! :wave:**__',

            'bad_guild': 'Le serveur discord choisi n\'existe pas, ou Hades9000 n\'y est pas installé. Vérifiez l\'ID de votre serveur et que Hades9000 l\'a bien rejoint.',
            'bad_notif_channel_error': 'Le channel de notifications avec l\'ID %s n\'existe pas sur ce serveur. Merci de le reparamètrer sur le site.',
            'bad_management_channel_error': 'Le channel de management avec l\'ID %s n\'existe pas sur ce serveur. Merci de le reparamètrer sur le site.',
            'bad_command': 'La commande "%s" est invalide. Entrez "$help" pour voir la liste des commandes disponibles',
            'inactive_command': 'La commande "%s" est dans le module `%s`, qui est désactivé pour ce serveur. Utilisez `$togglemodule %s` pour l\'activer',
            'bad_arguments': 'Arguments invalides pour la commande "%s"',
            'permission_denied': 'Vous n\'avez pas les permissions nécéssaires pour effectuer cette action. Rôle minimal : %s',
        }
    }
