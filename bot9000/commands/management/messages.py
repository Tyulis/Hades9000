import pytz
import asyncio
import discord
import datetime
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_del (Bot9000Command):
    name = 'del'
    minimum_role = 'moderator'
    arguments = ('number', '?user|u', '?before|b', '?after|a')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        channel = message.channel
        if arguments.number == 'all':
            number = None
        elif arguments.number.isdigit():
            number = int(arguments.number)
        else:
            tmpmessage = await channel.send(cls.string('bad_number', player.language))
            await asyncio.sleep(3)
            await tmpmessage.delete()
        if arguments.user is not None:
            user = bot.get_member(arguments.user, message.guild)
        else:
            user = None
        if arguments.before is not None:
            before = datetime.datetime.strptime(arguments.before, '%d-%m-%Y_%H:%M') - player.utcoffset()
        else:
            before = None
        if arguments.after is not None:
            after = datetime.datetime.strptime(arguments.after, '%d-%m-%Y_%H:%M') - player.utcoffset()
        else:
            after = None
        counter = 0
        async for message in channel.history(limit=(number + 1 if number is not None else None), before=before, after=after):
            if (user is not None and message.author == user) or user is None:
                await message.delete()
                counter += 1
        tmpmessage = await channel.send(cls.string('done', player.language) % (counter - 1))
        await asyncio.sleep(3)
        await tmpmessage.delete()

    strings = {
        'FR': {
            'help': '**$del <number> [-u <user>] [-a <after>] [-b <before>]** : Supprime des messages. <number> est le nombre de messages à supprimer, ou "all" pour supprimer tous les messages concernés. -u <utilisateur> permet de ne supprimer que les messages d\'un utilisateur en particulier, -a JJ-MM-AA_hh:mm permet de supprimer seulement les messages postés après la date donnée et -b JJ-MM-AA_hh:mm permet de ne supprimer que les messages supprimés avant la date donnée.',
            'description': 'Supprime des messages',
            'bad_date': 'La date doit être formatée comme suit : JJ-MM-AA_hh:mm',
            'bad_number': 'Le nombre de messages doit être "all" pour supprimer tous les messages concernés, ou un nombre pour supprimer un certain nombre de messages au maximum.',
            'done': '%d messages ont été supprimés',
        }
    }
