# -*- coding:utf-8 -*-

import pytz
import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_playerinfo (Bot9000Command):
    name = 'playerinfo'
    minimum_role = 'member'
    arguments = ('?user', '?/timezone|t', '?/corp|c', '?/language|l', '?/level|v', '?/rslevel|r', '?/influence|i')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.user is None:
            if player.discordid is not None:
                targetplayer = player
            else:
                await message.channel.send(cls.string('not_registered', player.language))
                return
        else:
            try:
                targetplayer = Player.objects.get(name=arguments.user)
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('unknown_player', player.language) % arguments.user)
                return
        all = (not arguments.corp) and (not arguments.timezone) and (not arguments.language) and (not arguments.level) and (not arguments.rslevel) and (not arguments.influence)
        if not targetplayer.corp.group == player.corp.group and not targetplayer.publicprofile:
            await message.channel.send(cls.string('not_public', player.language) % targetplayer.name)
            return
        response = cls.string('introduction', player.language) % targetplayer.name
        if all or arguments.corp:
            response += cls.string('corp', player.language) % targetplayer.corp.name
        if all or arguments.level:
            response += cls.string('level', player.language) % targetplayer.level()
        if all or arguments.rslevel:
            response += cls.string('rslevel', player.language) % targetplayer.rslevel()
        if all or arguments.influence:
            response += cls.string('influence', player.language) % targetplayer.influence()
        if all or arguments.language:
            response += cls.string('language', player.language) % targetplayer.language
        if all or arguments.timezone:
            response += cls.string('timezone', player.language) % (targetplayer.timezone, targetplayer.utcoffset())
        await message.channel.send(response)


    strings = {
        'FR':{
            'help': '**$playerinfo [<name>] [-t] [-c] [-l] [-r] [-v] [-i]** : Renvoie des informations sur l\'utilisateur. Renvoie les vôtres si le nom n\'est pas précisé. Si aucune autre option n\'est précisée, renvoie toutes les infos. Sinon, ajoutez -c pour la corporation, -l pour la langue, -v pour le niveau, -r pour le niveau de RS, -i pour l\'influence et -t pour la timezone',
            'description': 'Donne des informations sur un joueur',
            'not_registered': 'Vous n\'êtes pas enregistré par Hades9000',
            'unknown_player': 'Le joueur %s est inconnu',
            'not_public': 'Le profil du joueur %s n\'est pas public',
            'introduction': '**__Informations sur %s__**\n',
            'timezone': '**Timezone** : %s (UTC+ %s)\n',
            'language': '**Langage** : %s\n',
            'corp': '**Corporation** : %s\n',
            'level': '**Niveau** : %s\n',
            'rslevel': '**Niveau de RS** : %s\n',
            'influence': '**Influence** : %s\n',
        }
    }


class cmd_setinfo (Bot9000Command):
    name = 'setinfo'
    minimum_role = 'member'
    arguments = ('?timezone|t', '?language|l', '?rslevel|r', '?level|v', '?influence|i')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.timezone is not None:
            tzname = arguments.timezone
            if tzname not in pytz.common_timezones:
                await message.channel.send(cls.string('bad_timezone', player.language) % tzname)
            else:
                player.timezone = tzname
        if arguments.language is not None:
            if len(arguments.language) != 2:
                await message.channel.send(cls.string('bad_language', player.language))
            else:
                player.language = arguments.language.upper()
        update = PlayerUpdate.new(player)
        updated = False
        if arguments.rslevel is not None:
            if arguments.rslevel.isdigit():
                level = int(arguments.rslevel)
                if 0 < level <= max_rslevel:
                    update.rslevel = level
                    updated = True
                else:
                    await message.channel.send(cls.string('bad_rslevel', player.language))
            else:
                await message.channel.send(cls.string('bad_rslevel', player.language))
        if arguments.level is not None:
            if arguments.level.isdigit():
                level = int(arguments.level)
                update.level = level
                updated = True
            else:
                await message.channel.send(cls.string('bad_level', player.language))
        if arguments.influence is not None:
            if arguments.influence.isdigit():
                influence = int(arguments.influence)
                update.influence = influence
                updated = True
            else:
                await message.channel.send(cls.string('bad_influence', player.language))
        player.save()
        if updated:
            update.save()
        await message.channel.send(cls.string('done', player.language))

    strings = {
        'FR': {
            'help': '**$setinfo [-t <timezone>] [-l <language>] [-r <rslevel>] [-v <level>] [-i <influence>]** : Change les informations de son compte',
            'description': 'Permet de changer les informations de son compte',
            'bad_timezone': 'La timezone %s est invalide. Entrez `$data timezones` pour la liste des timezones diponibles, ou modifiez-la sur le site',
            'bad_language': 'Le code de la langue doit être un code à 2 lettres (exemples : FR, EN, RU, ...)',
            'bad_rslevel': 'Le niveau de RS doit être un nombre entre 1 et 10',
            'bad_level': 'Le niveau d\'expérience doit être un nombre !',
            'bad_influence': 'L\'influence doit être un nombre !',
            'done': 'Les informations ont été mises à jour',
        }
    }
