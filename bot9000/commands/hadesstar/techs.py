# -*- coding:utf-8 -*-

import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_techs (Bot9000Command):
    name = 'techs'
    minimum_role = 'member'
    arguments = ('?user|u', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.user is None:
            targetplayer = player
        else:
            try:
                targetplayer = Player.objects.get(name=arguments.user)
                if targetplayer.corp.group != player.corp.group:
                    await bot.send_message(message.channel, cls.string('not_same_group', player.language))
                    return
            except ObjectDoesNotExist:
                await bot.send_message(message.channel, cls.string('unknown_player', player.language) % arguments.user)
                return
        response = cls.string('introduction', player.language) % targetplayer.name
        response += cls.string('ships_introduction', player.language)

        totalscore = 0
        wstotalscore = 0
        shiplevels = targetplayer.shiplevels()
        for shiptype in ship_names:
            level = shiplevels[shiptype]
            score = ship_score(shiptype, level)
            wsscore = ship_wspoints[shiptype][level]
            wstotalscore += wsscore
            totalscore += score
            response += cls.string('ship', player.language) % (ship_names[shiptype], level, score, wsscore)

        response += cls.string('modules_introduction', player.language)

        modulelevels = targetplayer.getmodules()
        for modulecode in modulelevels:
            if modulelevels[modulecode] > 0:
                level = modulelevels[modulecode]
                score = module_score(modulecode, level)
                totalscore += score
                wsscore = moduledata[modulecode][level - 1]['WhiteStarScore']
                if wsscore is not None:
                    wstotalscore += wsscore
                response += cls.string('module', player.language) % (module_names[modulecode], level, score, (wsscore if wsscore is not None else '-'))

        response += cls.string('totalscores', player.language) % (totalscore, wstotalscore)
        await bot.send_split(message.channel, response)

    strings = {
        'FR': {
            'help': '**$techs [-u <user>]** : Affiche les techs de l\'utilisateur sélectionné, ou les vôtres si l\'utilisateur n\'est pas spécifié',
            'description': 'Affiche les techs d\'un joueur',
            'not_same_group': 'Vous ne pouvez pas voir les techs des joueurs d\'un autre groupe',
            'unknown_player': 'Le joueur %s est inconnu',
            'introduction': '**__Techs de %s__**\n',
            'ships_introduction': '\n**__Vaisseaux__**\n',
            'ship': '__%s__ : **Niveau %d** (%d pts / %d WS)\n',
            'modules_introduction': '\n**__Modules__**\n',
            'module': '__%s__ : **Niveau %d** (%d pts / %s WS)\n',
            'totalscores': '\n**Score total** : %d pts\n**Score WS** : %d pts',
        }
    }


class cmd_ships (Bot9000Command):
    name = 'ships'
    minimum_role = 'member'
    arguments = ('?user|u', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.user is None:
            targetplayer = player
        else:
            try:
                targetplayer = Player.objects.get(name=arguments.user)
                if targetplayer.corp.group != player.corp.group:
                    await bot.send_message(message.channel, cls.string('not_same_group', player.language))
                    return
            except ObjectDoesNotExist:
                await bot.send_message(message.channel, cls.string('unknown_player', player.language) % arguments.user)
                return
        response = cls.string('introduction', player.language) % targetplayer.name
        modlevels = targetplayer.getmodules()
        for ship in sorted(targetplayer.ships(), key=lambda s: s['id']):
            score = 0
            wsscore = 0
            shipmods = []
            for module in ship['trade'] + ship['mining'] + ship['weapon'] + ship['shield'] + ship['support']:
                if module.endswith('.none'):
                    continue
                score += module_score(module, modlevels[module])
                wsmodscore = moduledata[module][modlevels[module] - 1]['WhiteStarScore']
                if wsmodscore is not None:
                    wsscore += wsmodscore
                shipmods.append(cls.string('shipmod', player.language) % (module_names[module], modlevels[module]))
            response += cls.string('ship', player.language) % (ship['id'], ship['name'], ship_names[ship['type']], ', '.join(shipmods), score, wsscore)
        await bot.send_split(message.channel, response)


    strings = {
        'FR': {
            'help': '**$techs [-u <user>]** : Affiche les vaisseaux de l\'utilisateur sélectionné, ou les vôtres si l\'utilisateur n\'est pas spécifié',
            'description': 'Affiche les vaisseaux d\'un joueur',
            'not_same_group': 'Vous ne pouvez pas voir les vaisseaux des joueurs d\'un autre groupe',
            'unknown_player': 'Le joueur %s est inconnu',
            'introduction': '**__Vaisseaux de %s__**\n',
            'ship': 'ID %d : **%s** (%s) : %s (%d pts, %s WS)\n',
            'shipmod': '**%s** niv. **%d**',
        }
    }
