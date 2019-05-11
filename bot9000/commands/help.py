# -*- coding:utf-8 -*-

import os
import discord
from .base import *


class cmd_help (Bot9000Command):
    name = 'help'
    minimum_role = 'anyone'
    arguments = ('?command|c', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.command is None:
            response = cls.string('all_introduction', player.language)
            for command in bot.all_commands(group):
                response += '- **__%s__** : %s\n' % (command.name, command.description(player.language))
            response += cls.string('all_footer', player.language)
        else:
            command = bot.get_command(arguments.command, group)
            if isinstance(command, str):
                if command == 'unknown':
                    await message.channel.send(cls.string('bad_command', player.language) % arguments.command)
                elif command.startswith('inactive'):
                    module = command.split()[1]
                    await message.channel.send(cls.string('inactive_command', player.language) % (arguments.command, module, bot.make_url('editgroup'), module))
                return
            else:
                response = cls.string('command_introduction', player.language) % command.name + command.description(player.language) + '\n' + command.help(player.language)
        await bot.send_split(message.channel, response)


    strings = {
        'FR': {
            'help': '**$help** : Donne la liste des commandes disponibles\n**$help -c <commande>** : Donne de l \'aide à propos de la commande',
            'description': 'Aide sur les commandes',
            'all_introduction': '**__Commandes disponibles__** :\n\n',
            'all_footer': '*Vous pouvez entrer $help -c <commande> pour obtenir de l\'aide sur une commande spécifique*',
            'command_introduction': '**__Aide sur la commande %s__**\n',
            'bad_command': 'La commande "%s" est invalide. Entrez "$help" pour voir la liste des commandes disponibles',
            'inactive_command': 'La commande "%s" est dans le module `%s`, qui est désactivé pour ce serveur. Utilisez l\'interface d\'administration à %s ou `$togglemodule %s` pour l\'activer',
        }
    }


class cmd_sitelink (Bot9000PrintCommand):
    name = 'sitelink'
    minimum_role = 'anyone'
    arguments = ()
    parser = None

    strings = {
        'FR': {
            'help': '**$sitelink** : Donne le lien du site Hades9000',
            'description': 'Donne le lien du site Hades9000',
            'message': os.environ.get('SITE_URL'),
        }
    }

class cmd_hello (Bot9000PrintCommand):
    name = 'hello'
    minimum_role = 'anyone'
    arguments = ()
    parser = None

    strings = {
        'FR': {
            'help': '**$hello** : Dit bonjour pour tester si Hades9000 est fonctionnel',
            'description': 'Dit bonjour pour tester si Hades9000 est fonctionnel',
            'message': 'Bonjour. Je suis Hades9000, votre assistant de bord. Veuillez entrer `$help` pour plus d\'informations.',
        }
    }
