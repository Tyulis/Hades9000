# -*- coding:utf-8 -*-

import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_techs (Bot9000Command):
    name = 'techs'
    minimum_role = 'member'
    arguments = ('?user|u', '?/ids|i')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.user is None:
            targetplayer = player
        else:
            try:
                targetplayer = Player.objects.get(name=arguments.user)
                if targetplayer.corp.group != player.corp.group:
                    await message.channel.send(cls.string('not_same_group', player.language))
                    return
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('unknown_player', player.language) % arguments.user)
                return
        response = cls.string('introduction', player.language) % targetplayer.name
        response += cls.string('ships_introduction', player.language)

        totalscore = 0
        wstotalscore = 0
        blstotalscore = 0
        modulelevels = targetplayer.getmodules()
        shiplevels = targetplayer.shiplevels()
        for shiptype in ship_types:
            level = shiplevels[shiptype]
            score = ship_score(shiptype, level)
            wsscore = ship_data(shiptype, level, 'WhiteStarScore')
            blsscore = ship_data(shiptype, level, 'BSScore')
            wstotalscore += wsscore
            if blsscore is not None:
                blstotalscore += blsscore
            totalscore += score
            if shiptype == 'ship.player.transport':
                specific = cls.string('capacity', player.language) % transport_capacity(level, modulelevels['module.trade.extension'])
            else:
                specific = ''
            if arguments.ids:
                response += cls.string('ship_withid', player.language) % (ship_names[player.language][shiptype], shiptype, level, score, wsscore, (blsscore if blsscore is not None else '-'), specific)
            else:
                response += cls.string('ship', player.language) % (ship_names[player.language][shiptype], level, score, wsscore, (blsscore if blsscore is not None else '-'), specific)

        response += cls.string('modules_introduction', player.language)

        for modulecode in modulelevels:
            if modulelevels[modulecode] > 0:
                level = modulelevels[modulecode]
                score = module_score(modulecode, level)
                totalscore += score
                wsscore = module_data(modulecode, level, 'WhiteStarScore')
                blsscore = module_data(modulecode, level, 'BSScore')
                if wsscore is not None:
                    wstotalscore += wsscore
                if blsscore is not None:
                    blstotalscore += blsscore
                if arguments.ids:
                    response += cls.string('module_withid', player.language) % (module_names[player.language][modulecode], modulecode, level, score, (wsscore if wsscore is not None else '-'), (blsscore if blsscore is not None else '-'))
                else:
                    response += cls.string('module', player.language) % (module_names[player.language][modulecode], level, score, (wsscore if wsscore is not None else '-'), (blsscore if blsscore is not None else '-'))

        response += cls.string('totalscores', player.language) % (totalscore, wstotalscore)
        await bot.send_split(message.channel, response)

    strings = {
        'FR': {
            'help': '**$techs [-u <user>] [-i]** : Affiche les techs de l\'utilisateur sélectionné, ou les vôtres si l\'utilisateur n\'est pas spécifié. Ajoutez -i pour voir les identifiants comme utilisés par `$settech` et affichés par `$techids`',
            'description': 'Affiche les techs d\'un joueur',
            'not_same_group': 'Vous ne pouvez pas voir les techs des joueurs d\'un autre groupe',
            'unknown_player': 'Le joueur %s est inconnu',
            'introduction': '**__Techs de %s__**\n',
            'ships_introduction': '\n**__Vaisseaux__**\n',
            'ship': '__%s__ : **Niveau %d** (%d pts / %d WS / %s EB)%s\n',
            'ship_withid': '__%s__ *[%s]* : **Niveau %d** (%d pts / %d WS / %s EB)%s\n',
            'modules_introduction': '\n**__Modules__**\n',
            'module': '__%s__ : **Niveau %d** (%d pts / %s WS / %s EB)\n',
            'module_withid': '__%s__ *[%s]* : **Niveau %d** (%d pts / %s WS / %s EB)\n',
            'totalscores': '\n**Score total** : %d pts\n**Score WS** : %d pts\n',
            'capacity': ', %dt',
        }
    }

class cmd_techids (Bot9000Command):
    name = 'techids'
    minimum_role = 'anyone'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        response = ''
        for key, name in module_names[player.language].items():
            if '.cerberus.' not in key and '.none' not in key:
                response += '__**%s**__ : *%s*\n' % (name, key)
        await bot.send_split(message.channel, response)

    strings = {
        'FR': {
            'help': '**$techids** : Affiche les identifiants de techs pour une utilisation plus facile de `$settech`',
            'description': 'Affiche les identifiants de techs pour une utilisation plus facile de `$settech`',
        }
    }

class cmd_settech (Bot9000Command):
    name = 'settech'
    minimum_role = 'member'
    arguments = ('tech', 'level')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        for key, name in module_names[player.language].items():
            if arguments.tech.lower() in (key, name.lower()):
                tech = key
                break
        else:
            for key, name in ship_names[player.language].items():
                if arguments.tech.lower() in (key, name.lower()):
                    tech = key
                    break
            else:
                await message.channel.send(cls.string('unknown_tech', player.language) % arguments.tech)
                return
        if not arguments.level.isdigit():
            await message.channel.send(cls.string('bad_number', player.language))
            return
        level = int(arguments.level)

        update = PlayerUpdate.new(player)
        if tech.startswith('module.') and not tech.startswith('module.cerberus') and '.none' not in tech:
            if level < 0 or level > len(_MODULE_DATA[tech]):
                await message.channel.send(cls.string('bad_level', player.language) % (0, _MODULE_DATA[tech]))
                return
            update.setmodule(tech, level)
        elif tech.startswith('ship.player.'):
            if level < 1 or level > len(_SHIP_DATA[tech]):
                await message.channel.send(cls.string('bad_level', player.language))
                return
            if tech == 'ship.player.battleship':
                update.bslevel = level
            elif tech == 'ship.player.miner':
                update.fslevel = level
            elif tech == 'ship.player.transport':
                update.tslevel = level
        else:
            await message.channel.send(cls.string('bad_tech', player.language) % tech)
            return
        update.save()
        await message.channel.send(cls.string('done', player.language) % (tech, level))


    strings = {
        'FR': {
            'help': '**$settech <tech> <level>** : Change le niveau d\'un module ou d\'un vaisseau. Exemple : `$settech canon 9`, `$settech cuirassé 5`, `$settech module.trade.dispatch 4`',
            'description': 'Change le niveau d\'une technologie',
            'unknown_tech': 'La technologie %s est inconnue. Entrez `$techids` pour voir les techs disponibles ou utilisez l\'app web.',
            'bad_number': 'Le niveau doit être un nombre',
            'bad_level': 'Ce niveau est impossible',
            'bad_tech': 'La technologie %s est invalide',
            'done': 'La technologie *%s* a bien été changée pour le niveau %d',
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
                    await message.channel.send(cls.string('not_same_group', player.language))
                    return
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('unknown_player', player.language) % arguments.user)
                return
        response = cls.string('introduction', player.language) % targetplayer.name
        modlevels = targetplayer.getmodules()
        shiplevels = targetplayer.shiplevels()
        for ship in sorted(targetplayer.ships(), key=lambda s: s['id']):
            score = ship_score(ship['type'], shiplevels[ship['type']])
            wsscore = ship_data(ship['type'], shiplevels[ship['type']], 'WhiteStarScore')
            wsscore = 0 if wsscore is None else wsscore
            blsscore = ship_data(ship['type'], shiplevels[ship['type']], 'BSScore')
            blsscore = 0 if blsscore is None else blsscore
            shipmods = []
            for module in ship['trade'] + ship['mining'] + ship['weapon'] + ship['shield'] + ship['support']:
                if module.endswith('.none'):
                    continue
                score += module_score(module, modlevels[module])
                wsmodscore = module_data(module, modlevels[module], 'WhiteStarScore')
                blsmodscore = module_data(module, modlevels[module], 'BSScore')
                if wsmodscore is not None:
                    wsscore += wsmodscore
                if blsmodscore is not None:
                    blsscore += blsmodscore
                shipmods.append(cls.string('shipmod', player.language) % (module_names[player.language][module], modlevels[module]))

            potential = potential_consumption(ship, shiplevels[ship['type']], modlevels)
            if ship['type'] == 'ship.player.battleship':
                response += cls.string('battleship', player.language) % (ship['id'], ship['name'], ship_names[player.language][ship['type']], ', '.join(shipmods), score, wsscore, blsscore, potential)
            elif ship['type'] == 'ship.player.transport':
                capacity = transport_capacity(shiplevels[ship['type']], modlevels['module.trade.extension'] if 'module.trade.extension' in ship['trade'] else 0)
                bonus = (transport_bonus(ship, modlevels) - 1) * 100
                response += cls.string('transport', player.language) % (ship['id'], ship['name'], ship_names[player.language][ship['type']], ', '.join(shipmods), score, wsscore, potential, capacity, bonus)
            elif ship['type'] == 'ship.player.miner':
                capacity = miner_capacity(shiplevels[ship['type']], modlevels['module.mining.extension'] if 'module.mining.extension' in ship['mining'] else 0)
                speed = miner_speed(ship, shiplevels[ship['type']], modlevels)
                response += cls.string('miner', player.language) % (ship['id'], ship['name'], ship_names[player.language][ship['type']], ', '.join(shipmods), score, wsscore, potential, capacity, speed)
        await bot.send_split(message.channel, response)


    strings = {
        'FR': {
            'help': '**$ships [-u <user>]** : Affiche les vaisseaux de l\'utilisateur sélectionné, ou les vôtres si l\'utilisateur n\'est pas spécifié',
            'description': 'Affiche les vaisseaux d\'un joueur',
            'not_same_group': 'Vous ne pouvez pas voir les vaisseaux des joueurs d\'un autre groupe',
            'unknown_player': 'Le joueur %s est inconnu',
            'introduction': '**__Vaisseaux de %s__**\n',
            'transport': 'ID %d : **%s** (%s) : %s\n        %d pts, %s WS, %d CP15\n        %dt, %.1f%% bonus\n',
            'miner': 'ID %d : **%s** (%s) : %s\n        %d pts, %s WS, %d CP15\n        %dH, %dH/min/roid\n',
            'battleship': 'ID %d : **%s** (%s) : %s\n        %d pts, %s WS, %s EB, %d CP15\n',
            'shipmod': '**%s** niv. **%d**',
        }
    }

class cmd_techlist (Bot9000Command):
    name = 'techlist'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        response = ''
        for member in group.members():
            response += '**%s** : %d pts, %d WS\n' % (member.name, member.techscore(), member.wsscore())
        await bot.send_split(message.channel, response)

    strings = {
        'FR': {
            'help': '**$techlist** : Liste les scores de tous les membres du groupe',
            'description': 'Liste les scores de tous les membres du groupe',
        }
    }
