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
                    await message.channel.send(cls.string('ws_private', player.language) % arguments.corporation)
                    return
                corps = [corp]
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('unknown_corp', player.language) % arguments.corporation)
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
        await message.channel.send(response)

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
                await message.channel.send(cls.string('choose_corp', player.language))
                return
            else:
                corp = group.corporations()[0]
        else:
            try:
                corp = Corporation.objects.get(name=arguments.corporation)
                if corp.group != group:
                    await message.channel.send(cls.string('foreign_corp', player.language) % arguments.corporation)
                    return
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('unknown_corp', player.language) % arguments.corporation)
                return
        if arguments.launch is not None:
            try:
                launchdate = datetime.datetime.strptime(arguments.launch, '%d/%m/%Y-%H:%M').astimezone(player.tzinfo()) - player.utcoffset()
            except ValueError:
                await message.channel.send(cls.string('bad_datetime_format', player.language))
                return
        else:
            launchdate = datetime.datetime.now(tz=player.tzinfo())
        name = (arguments.name if arguments.name is not None else cls.string('default_name', group.language) % (corp.name, launchdate.strftime('%d/%m/%Y')))
        comment = (arguments.comment if arguments.comment is not None else '')
        state = 'ws.state.inscriptions' if arguments.startregister else 'ws.state.future'
        ws = WS(corp=corp, name=name, start=launchdate, state=state)
        ws.save()
        await message.channel.send(cls.string('done', player.language) % (ws.id, bot.make_url('ws/%d' % ws.id)))

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
            await message.channel.send(cls.string('not_a_number', player.language))
            return
        try:
            ws = WS.objects.get(id=wsid)
            if ws.corp.group != group and not ws.corp.group.publicws:
                await message.channel.send(cls.string('foreign_corp', player.language) % wsid)
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_ws', player.language) % wsid)
            return
        response = cls.string('introduction', player.language) % wsid
        response += cls.string('corps', player.language) % (ws.corp.name, ws.score, ws.opponentscore, ws.opponentcorp)
        start = ws.start.astimezone(player.tzinfo()).strftime('%d/%m/%Y - %H:%M')
        end = ws.end().astimezone(player.tzinfo()).strftime('%d/%m/%Y - %H:%M')
        response += cls.string('dates', player.language) % (start, end)
        response += cls.string('state', player.language) % ws_states[ws.state]
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
                                modules.append('*%s* (niv. %d)' % (module_names[player.language][module], modlevels[module]))
                        response += cls.string('ship', player.language) % (ship['name'], ship_names[player.language][ship['type']], ', '.join(modules))
        response += cls.string('totalstats', player.language) % totalscore
        await message.channel.send(response)

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
            'state': 'État : %s\n',
            'player_intro': '\n**__%s__** : *%d pts WS*\n',
            'ship': '__%s__ (%s): %s\n',
            'totalstats': '\n*Score WS total : %d pts*',
        }
    }


class cmd_wsregister (Bot9000Command):
    name = 'wsregister'
    minimum_role = 'member'
    arguments = ('wsid', ',ships')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.wsid.isdigit():
            await message.channel(cls.string('bad_wsid', player.language) % arguments.wsid)
            return
        wsid = int(arguments.wsid)
        if not all(map(str.isdigit, arguments.ships)):
            await message.channel.send(cls.string('bad_shipid', player.language))
            return
        shipids = tuple(map(int, arguments.ships))
        try:
            ws = WS.objects.get(id=wsid)
            if ws.corp.group != group:
                await message.channel.send(cls.string('foreign_ws', player.language) % wsid)
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_ws', player.language) % wsid)
            return
        try:
            wsmember = WSPlayer.objects.get(update__player=player)
            if ws.state in ('ws.state.future', 'ws.state.ended'):
                await message.channel.send(cls.string('forbidden_edit', player.language))
                return
        except ObjectDoesNotExist:
            if ws.state != 'ws.state.inscriptions':
                await message.channel.send(cls.string('inscriptions_closed', player.language))
                return
            wsmember = WSPlayer(ws=ws)
        wsmember.ws = ws
        wsmember.initdispos(start=ws.start)
        wsmember.setships(shipids)
        wsmember.save()
        await message.channel.send(cls.string('done', player.language) % wsid)

    strings = {
        'FR': {
            'help': '**$wsregister <ws-id> <ship-id> [<ship-id> ...]** : Inscrit pour la WS sélectionnée (ID donné par `$wslist`), avec les vaisseaux sélectionnés (IDs donnés par `$ships`)',
            'description': 'Inscrit à une WS',
            'bad_wsid': '"%s" n\'est pas un ID de WS valide. Vous pouvez récupérer les IDs de WS avec la commande `$wslist`',
            'bad_shipid': 'Les IDs de vaisseaux doivent être des nombres, utilisez `$ships` pour les voir',
            'foreign_ws': 'La WS n°%d n\'est pas dans ce groupe. Utilisez `$wslist` pour voir les IDs de WS',
            'unknown_ws': 'La WS n°%d est inconnue. Utilisez `$wslist` pour voir les IDs de WS',
            'forbidden_edit': 'Vous ne pouvez pas modifier votre inscription à cette WS',
            'inscriptions_closed': 'Les inscriptions à cette WS sont fermées',
            'done': 'Votre inscription à la WS n°%d a bien été enregistrée !',
        }
    }

class cmd_wsstate (Bot9000Command):
    name = 'wsstate'
    minimum_role = 'responsible'
    arguments = ('wsid', 'state')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        stateid = 'ws.state.' + arguments.state
        if stateid not in ws_states:
            await message.channel.send(cls.string('bad_state', player.language))
            return
        if not arguments.wsid.isdigit():
            await message.channel(cls.string('bad_wsid', player.language) % arguments.wsid)
            return
        wsid = int(arguments.wsid)
        try:
            ws = WS.objects.get(id=wsid)
            if ws.corp.group != player.corp.group:
                await message.channel.send(cls.string('foreign_ws', player.language) % wsid)
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_ws', player.language) % wsid)
            return
        ws.state = stateid
        ws.save()
        await message.channel.send(cls.string('done', player.language) % arguments.state)

    strings = {
        'FR': {
            'help': '**$wsstate <id> <state>** : Change l\'état d\'une étoile blanche. Utilise l\'ID donné par `$wslist`. L\'état doit être `future` pour une WS future, `inscriptions` si les inscriptions sont ouvertes, `idle` si les inscriptions sont fermées, `running` si la WS est en cours et `ended` si elle est terminée',
            'description': 'Change l\'état d\'une étoile blanche',
            'bad_state': 'L\'état doit être `future`, `inscriptions`, `idle`, `running` ou `ended`',
            'bad_wsid': '"%s" n\'est pas un ID de WS valide. Vous pouvez récupérer les IDs de WS avec la commande `$wslist`',
            'foreign_ws': 'La WS n°%d n\'est pas dans ce groupe. Utilisez `$wslist` pour voir les IDs de WS',
            'unknown_ws': 'La WS n°%d est inconnue. Utilisez `$wslist` pour voir les IDs de WS',
            'done': 'La WS a bien été changée à l\'état %s',
        }
    }

class cmd_wsrun (Bot9000Command):
    name = 'wsrun'
    minimum_role = 'responsible'
    arguments = ('wsid', '?/force|f')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.wsid.isdigit():
            await message.channel(cls.string('bad_wsid', player.language) % arguments.wsid)
            return
        wsid = int(arguments.wsid)
        try:
            ws = WS.objects.get(id=wsid)
            if ws.corp.group != player.corp.group:
                await message.channel.send(cls.string('foreign_ws', player.language) % wsid)
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_ws', player.language) % wsid)
            return
        if ws.state in ('ws.state.running', 'ws.state.ended'):
            await message.channel.send(cls.string('bad_state', player.language))
            return
        members = ws.players()
        if len(members) not in (5, 10, 15) and not arguments.force:
            await message.channel.send(cls.string('bad_rostersize', player.language) % len(members))
            return
        wsroleid = (ws.corp.ws1role if ws.slot == 1 else ws.corp.ws2role)
        leadroleid = (ws.corp.lead1role if ws.slot == 1 else ws.corp.lead2role)
        wsrole = discord.utils.get(message.guild.roles, id=wsroleid)
        leadrole = discord.utils.get(message.guild.roles, id=leadroleid)
        if wsrole is None:
            await message.channel.send(cls.string('no_wsrole', player.language) % (ws.slot, ws.corp.name, ws.slot))
        if leadrole is None:
            await message.channel.send(cls.string('no_leadrole', player.language) % (ws.slot, ws.corp.name, ws.slot))
        for player in members:
            discorduser = discord.utils.get(message.guild.members, id=player.discordid)
            roles = []
            if wsrole is not None:
                roles.append(wsrole)
            if leadrole is not None and ws.lead == player:
                roles.append(leadrole)
            await discorduser.add_roles(*roles)
        ws.state = 'ws.state.running'
        ws.save()
        await message.channel.send(cls.string('done', player.language))

    strings = {
        'FR': {
            'help': '**$wsrun <id> [-f]** : Lance une étoile blanche et attribue les rôles correspondants. N\'utilisez -f que pour forcer une taille de groupe de WS invalide',
            'description': 'Lance une étoile blanche',
            'bad_wsid': '"%s" n\'est pas un ID de WS valide. Vous pouvez récupérer les IDs de WS avec la commande `$wslist`',
            'foreign_ws': 'La WS n°%d n\'est pas dans ce groupe. Utilisez `$wslist` pour voir les IDs de WS',
            'unknown_ws': 'La WS n°%d est inconnue. Utilisez `$wslist` pour voir les IDs de WS',
            'bad_state': 'La WS a déjà été lancée ou est déjà terminée',
            'bad_rostersize': '%d joueurs sont inscrits à cette WS, ce qui ne correspond pas aux tailles standards 5, 10 ou 15 joueurs. Si c\'est normal, relancez cette commande avec l\'option `-f`',
            'no_wsrole': 'Il n\'y a aucun rôle associé aux joueurs de la WS %d (*%s:ws%d*)',
            'no_leadrole': 'Il n\'y a aucun rôle associé au lead de la WS %d (*%s:lead%d*)',
            'done': 'La WS a bien été lancée !',
        }
    }

class cmd_wsend (Bot9000Command):
    name = 'wsend'
    minimum_role = 'responsible'
    arguments = ('wsid', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.wsid.isdigit():
            await message.channel(cls.string('bad_wsid', player.language) % arguments.wsid)
            return
        wsid = int(arguments.wsid)
        try:
            ws = WS.objects.get(id=wsid)
            if ws.corp.group != player.corp.group:
                await message.channel.send(cls.string('foreign_ws', player.language) % wsid)
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_ws', player.language) % wsid)
            return
        if ws.state != 'ws.state.running':
            await message.channel.send(cls.string('bad_state', player.language))
            return
        members = ws.players()
        wsroleid = (ws.corp.ws1role if ws.slot == 1 else ws.corp.ws2role)
        leadroleid = (ws.corp.lead1role if ws.slot == 1 else ws.corp.lead2role)
        wsrole = discord.utils.get(message.guild.roles, id=wsroleid)
        leadrole = discord.utils.get(message.guild.roles, id=leadroleid)
        if wsrole is None:
            await message.channel.send(cls.string('no_wsrole', player.language) % (ws.slot, ws.corp.name, ws.slot))
        if leadrole is None:
            await message.channel.send(cls.string('no_leadrole', player.language) % (ws.slot, ws.corp.name, ws.slot))
        for player in members:
            discorduser = discord.utils.get(message.guild.members, id=player.discordid)
            roles = []
            if wsrole is not None:
                roles.append(wsrole)
            if leadrole is not None and ws.lead == player:
                roles.append(leadrole)
            await discorduser.remove_roles(*roles)
        ws.state = 'ws.state.ended'
        ws.save()
        ws.corp.relics += ws.score
        ws.corp.save()
        await message.channel.send(cls.string('done', player.language))

    strings = {
        'FR': {
            'help': '**$wsrun <id> [-f]** : Lance une étoile blanche et attribue les rôles correspondants. N\'utilisez -f que pour forcer une taille de groupe de WS invalide',
            'description': 'Termine une étoile blanche',
            'bad_wsid': '"%s" n\'est pas un ID de WS valide. Vous pouvez récupérer les IDs de WS avec la commande `$wslist`',
            'foreign_ws': 'La WS n°%d n\'est pas dans ce groupe. Utilisez `$wslist` pour voir les IDs de WS',
            'unknown_ws': 'La WS n°%d est inconnue. Utilisez `$wslist` pour voir les IDs de WS',
            'bad_state': 'La WS n\'est pas en cours',
            'bad_rostersize': '%d joueurs sont inscrits à cette WS, ce qui ne correspond pas aux tailles standards 5, 10 ou 15 joueurs. Si c\'est normal, relancez cette commande avec l\'option `-f`',
            'no_wsrole': 'Il n\'y a aucun rôle associé aux joueurs de la WS %d (*%s:ws%d*)',
            'no_leadrole': 'Il n\'y a aucun rôle associé au lead de la WS %d (*%s:lead%d*)',
            'done': 'La WS a bien été terminée !',
        }
    }
