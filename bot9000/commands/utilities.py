# -*- coding:utf-8 -*-

import pytz
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
