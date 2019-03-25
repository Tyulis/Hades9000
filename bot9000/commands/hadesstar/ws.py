# -*- coding:utf-8 -*-

import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_wslist (Bot9000Command):
    name = 'wslist'
    minimum_role = 'member'
    arguments = ('?corporation|c', '?/old|o')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.corporation is not None:
            try:
                corp = Corporation.objects.get(name=arguments.corporation)
                if not corp.group.publicws and corp.group != group:
                    await bot.send_message(message.channel, cls.string('ws_private', player.language) % arguments.corporation)
                    return
                corps = [corp]
            except ObjectDoesNotExist:
                await bot.send_mesage(message.channel, cls.string('unknown_corp', player.language) % arguments.corporation)
                return
        else:
            corps = group.corporations()
        wss = WS.objects.none()
        for corp in corps:
            wss = wss.union(WS.objects.filter(corp=corp))
        if not arguments.old:
            wss = [ws for ws in wss if ws.state != 'ws.state.ended']  # Bug with union + exclude ?!
        response = cls.string('introduction', player.language) % (corps[0].name if len(corps) <= 1 else group.name)
        for ws in wss:
            response += cls.string('ws', player.language) % (ws.id, ws.name, ws.start.astimezone(player.tzinfo()).strftime('%d/%m/%Y %H:%M'), ws_states[ws.state])
        await bot.send_message(message.channel, response)

    strings = {
        'FR': {
            'help': '**$wslist [-c <corporation>] [-o]** : Affiche la liste des WS futures ou en cours. Si la corporation n\'est pas spécifiée, affiche toutes celles du groupe. Si -o est ajouté, affiche toutes les WS, y compris les anciennes',
            'description': 'Liste les WS',
            'ws_private': 'Les WS de la corporation %s sont privées',
            'unknown_corp': 'La corporation %s est inconnue',
            'introduction': '***__WS de %s__***\n\n',
            'ws': 'ID %d : **%s** : le %s (%s)\n',
        }
    }


class cmd_wsinit (Bot9000Command):
    name = 'wsinit'
    minimum_role = 'responsible'
    arguments = ('?corporation|c', '?name|n', '?launch|l', '?comment|m', '?/startregister|s')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.corporation is None:
            if group.isgroup:
                await bot.send_message(message.channel, cls.string('choose_corp', player.language))
                return
            else:
                corp = group.corps()[0]
        else:
            try:
                corp = Corporation.objects.get(name=arguments.corporation)
                if corp.group != group:
                    await bot.send_message('foreign_corp', player.language) % arguments.corporation
                    return
            except ObjectDoesNotExist:
                await bot.send_message('unknown_corp', player.language) % arguments.corporation
                return
        if arguments.launch is not None:
            try:
                launchdate = datetime.datetime.strptime(arguments.launch, '%d/%m/%Y-%H:%M').astimezone(player.tzinfo()) - player.utcoffset()
            except ValueError:
                await bot.send_message('bad_datetime_format', player.language)
                return
        else:
            launchdate = datetime.datetime.now(tz=player.tzinfo())
        name = (arguments.name if arguments.name is not None else cls.string('default_name', group.language) % (corp.name, launchdate.strftime('%d/%m/%Y')))
        comment = (arguments.comment if arguments.comment is not None else '')
        state = 'ws.state.inscriptions' if arguments.startregister else 'ws.state.future'
        ws = WS(corp=corp, name=name, start=launchdate, state=state)
        ws.save()
        await bot.send_message(message.channel, cls.string('done', player.language) % (ws.id, bot.make_url('ws/%d' % ws.id)))

    strings = {
        'FR': {
            'help': '**$wsinit [-c <corporation>] [-n <name>] [-l <launchdate>] [-m <comment>] [-s]** : Crée une WS dans la <corporation>. Vous pouvez ajouter -n pour donner un nom à la WS, -l JJ/MM/AA-HH:MM pour spécifier une date de lancement prévue, -m pour ajouter un commentaire et -s pour lancer directement les inscriptions',
            'description': 'Crée une WS',
            'choose_corp': 'Ceci est le discord d\'un groupe, vous devez choisir la corporation où sera lancée la WS, avec l\'option `-c <corporation`',
            'foreign_corp': 'La corporation %s ne fait pas partie de ce groupe',
            'unknown_corp': 'La corporation %s est inconnue',
            'default_name': 'WS %s du %s',
            'bad_datetime_format': 'La date de lancement doit être exactement dans ce format : `JJ/MM/AA-hh:mm` (avec JJ le jour, MM le mois, AA l\'année, hh l\'heure et mm les minutes)',
            'done': 'La **WS n°%d** a bien été créée. Vous pouvez voir ou modifier les paramètres sur %s',
        }
    }


class cmd_wsinfo (Bot9000Command):
    name = 'wsinfo'
    minimum_role = 'member'
    arguments = ('id', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.id.isdigit():
            wsid = int(arguments.id)
        else:
            await bot.send_message(message.channel, cls.string('not_a_number', player.language))
            return
        try:
            ws = WS.objects.get(id=wsid)
            if ws.corp.group != group and not ws.corp.group.publicws:
                await bot.send_message(message.channel, cls.string('foreign_corp', player.language) % wsid)
                return
        except ObjectDoesNotExist:
            await bot.send_message(message.channel, cls.string('unknown_ws', player.language) % wsid)
            return
        response = cls.string('introduction', player.language) % wsid
        response += cls.string('corps', player.language) % (ws.corp.name, ws.score, ws.opponentscore, ws.opponentcorp)
        start = ws.start.astimezone(player.tzinfo()).strftime('%d/%m/%Y - %H:%M')
        end = ws.end().astimezone(player.tzinfo()).strftime('%d/%m/%Y - %H:%M')
        response += cls.string('dates', player.language) % (start, end)
        if ws.corp.group == group:
            totalscore = 0
            for wsplayer in ws.members():
                wsscore = wsplayer.update.wsscore()
                totalscore += wsscore
                response += cls.string('player_intro', player.language) % (wsplayer.update.player.name, wsscore)
                shipids = wsplayer.getships()
                modlevels = wsplayer.update.getmodules()
                for ship in wsplayer.update.getships():
                    if ship['id'] in shipids:
                        modules = []
                        for module in ship['trade'] + ship['mining'] + ship['weapon'] + ship['shield'] + ship['support']:
                            if not module.endswith('.none'):
                                modules.append('*%s* (niv. %d)' % (module_names[module], modlevels[module]))
                        response += cls.string('ship', player.language) % (ship['name'], ship_names[ship['type']], ', '.join(modules))
        response += cls.string('totalstats', player.language) % totalscore
        await bot.send_message(message.channel, response)

    strings = {
        'FR': {
            'help': '**$wsinfo <wsid>** : Affiche les informations d\'une WS. <wsid> doit être l\'ID de la WS affiché par la commande `$wslist`',
            'description': 'Donne les infos sur une WS',
            'not_a_number': 'Vous devez donner un ID comme un nombre, tel qu\'affiché par `$wslist`',
            'foreign_corp': 'La WS n°%d n\'est pas de votre groupe et n\'est pas publique',
            'unknown_ws': 'La WS n°%d n\'existe pas',
            'introduction': '**__WS n°%d__**\n',
            'corps': '**%s** %d - %d **%s**\n',
            'dates': 'De *%s* à *%s*\n',
            'player_intro': '\n**__%s__** : *%d pts WS*\n',
            'ship': '__%s__ (%s): %s\n',
            'totalstats': '\n*Score WS total : %d pts*',
        }
    }
