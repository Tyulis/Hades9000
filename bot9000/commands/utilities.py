# -*- coding:utf-8 -*-

import re
import pytz
import time
import datetime
import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from .base import Bot9000Command


class cmd_time (Bot9000Command):
    name = 'time'
    minimum_role = 'member'
    arguments = ('player', )
    parser = None

    _format = '%A %d/%m/%Y %H:%M:%S (%z)'

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            targetplayer = Player.objects.get(name=arguments.player)
        except ObjectDoesNotExist:
            discorduser = bot.get_member(arguments.player, message.guild)
            if discorduser is None:
                await message.channel.send(cls.string('unknown_player', player.language) % arguments.player)
                return
            try:
                targetplayer = Player.objects.get(discordid=discorduser.id)
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('not_signed_player', player.language) % arguments.player)
                return
        if targetplayer.corp.group != player.corp.group:
            await message.channel.send(cls.string('foreign_player', player.language) % arguments.player)
            return
        await message.channel.send(cls.string('response', player.language) % (player.name, player.timezone, player.datetime().strftime(cls._format), targetplayer.name, targetplayer.timezone, targetplayer.datetime().strftime(cls._format)))

    strings = {
        'FR': {
            'help': '**$time <joueur>** : Donne la date et l\'heure pour un autre joueur',
            'description': 'Donne la date et l\'heure pour un autre joueur',
            'unknown_player': 'Le joueur %s est inconnu dans ce groupe',
            'not_signed_player': 'Le joueur %s n\'est pas inscrit',
            'foreign_player': 'Le joueur %s ne fait pas partie de ce groupe',
            'response': '**%s** *(%s)* : %s\n**%s** *(%s)* : %s',
        }
    }


class cmd_afk (Bot9000Command):
    name = 'afk'
    minimum_role = 'member'
    arguments = ('time', )
    parser = None

    regex = re.compile(r'((\d+)[dj])?((\d+)[h])?((\d+)(m|min|mn))?')

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        timestring = arguments.time.replace(' ', '').strip().lower()
        match = re.match(cls.regex, timestring)
        if match is None:
            message.channel.send(cls.string('bad_time_format', player.language))
            return
        print(match.groups())
        groups = match.groups()
        days = int(groups[1] if groups[1] is not None else 0)
        hours = int(groups[3] if groups[3] is not None else 0)
        minutes = int(groups[5] if groups[5] is not None else 0)
        duration = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        player.afkduration = duration.total_seconds()
        player.afkstart = time.time()
        player.save()
        await message.channel.send(cls.string('done', player.language) % (player.name, days, hours, minutes))

    strings = {
        'FR': {
            'help': '**$afk <temps> : Vous spécifie absent pour un certain temps. Le temps doit avoir le format `2j2h2m`, `1j`, `3h20m`, ou autres combinaisons',
            'description': '$afk <temps> : Vous spécifie absent pour un certain temps',
            'bad_time_format': 'Le temps doit être dans le format `2j2h2m`',
            'done': '%s est AFK pour %d jours, %d heures, %d minutes',
        }
    }


class cmd_back (Bot9000Command):
    name = 'back'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        player.afkstart = -1
        player.afkduration = -1
        player.save()
        await message.channel.send(cls.string('done', player.language) % player.name)

    strings = {
        'FR': {
            'help': '**$back** : Termine une periode d\'absence',
            'description': 'Termine une période d\'absence',
            'done': '%s n\'est plus AFK',
        }
    }

class cmd_isafk (Bot9000Command):
    name = 'isafk'
    minimum_role = 'member'
    arguments = ('player', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if message.channel.id not in group.getafkchannels():
            await message.channel.send(cls.string('bad_channel', player.language))
            return
        discorduser = bot.get_member(arguments.player, message.guild)
        if discorduser is None:
            await message.channel.send(cls.string('unknown_user', player.language) % arguments.player)
            return
        try:
            target = Player.objects.get(discordid=discorduser.id)
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_user', player.language) % arguments.player)
            return
        if player.corp not in group.corporations():
            await message.channel.send(cls.string('not_allowed', player.language))
            return
        if target.afkstart == -1 and target.afkduration == -1:
            await message.channel.send(cls.string('not_afk', player.language) % target.name)
        elif target.afkstart + target.afkduration > time.time():
            remaining = target.afkstart + target.afkduration - time.time()
            days = remaining // (60 * 60 * 24)
            remaining %= (60 * 60 * 24)
            hours = remaining // (60 * 60)
            remaining %= (60 * 60)
            minutes = remaining // 60
            await message.channel.send(cls.string('afk', player.language) % (target.name, days, hours, minutes))
        else:
            excess = time.time() - (target.afkstart + target.afkduration)
            days = excess // (60 * 60 * 24)
            excess %= (60 * 60 * 24)
            hours = excess // (60 * 60)
            excess %= (60 * 60)
            minutes = excess // 60
            await message.channel.send(cls.string('still_afk', player.language) % (target.name, days, hours, minutes))

    strings = {
        'FR': {
            'help': '**$isafk <joueur>** : Donne les informations sur l\'absence d\'un joueur',
            'description' : 'Donne les informations sur l\'absence d\'un joueur',
            'bad_channel': 'Cette commande ne peut pas être utilisée dans ce channel',
            'unknown_user': 'L\'utilisateur %s est inconnu',
            'not_allowed': 'Vous n\'êtes pas autorisé à consulter cette information',
            'not_afk': '%s n\'est pas AFK',
            'afk': '%s est encore indiqué AFK pour %d jours, %d heures, %d minutes',
            'still_afk': '%s est AFK, et a indiqué revenir il y a %d jours, %d heures, %d minutes',
        }
    }
