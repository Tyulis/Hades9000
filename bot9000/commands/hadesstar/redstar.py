# -*- coding:utf-8 -*-

import discord
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import *
from main.models import *
from ..base import Bot9000Command


"""class cmd_rsin (Bot9000Command):
    name = 'rsin'
    minimum_role = 'member'
    arguments = ('level',)
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.level.isdigit():
            await message.channel.send(cls.string('bad_level', player.language))
            return
        level = int(arguments.level)
        if not (1 <= level <= 10):
            await message.channel.send(cls.string('bad_level', player.language))
            return
        try:
            rs = RedStar.objects.get(level=level, group=group)
        except ObjectDoesNotExist:
            rs = RedStar(group=group, level=level)
        try:
            already_rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
            print(already_rs)
            await message.channel.send(cls.string('already_in', player.language) % already_rs.level)
            return
        except ObjectDoesNotExist:
            pass
        if rs.player1 is None:
            rs.player1 = player
        elif rs.player2 is None:
            rs.player2 = player
        elif rs.player3 is None:
            rs.player3 = player
        elif rs.player4 is None:
            rs.player4 = player
        else:
            await message.channel.send(cls.string('queue_full', player.language))
            return
        player.rsready = False
        rs.save()
        users = [discord.utils.get(message.guild.members, id=rsplayer.discordid) for rsplayer in (rs.player1, rs.player2, rs.player3, rs.player4) if rsplayer is not None]
        players = '\n'.join(['- %s' % (discorduser.nick if discorduser.nick is not None else discorduser.name) for discorduser in users])
        await message.channel.send(cls.string('done', player.language) % (level, players))
        if len(rs.players()) >= 4:
            pings = ' '.join([discord.utils.get(message.guild.members, id=rsplayer.discordid).mention for rsplayer in rs.players()])
            await message.channel.send(cls.string('full_pings', group.language) % pings)


    strings = {
        'FR': {
            'help': '**$rsin <level> [-c <corporation>]** : Place dans la file de RS du niveau donné. Si la corporation n\'est pas spécifiée, utilise la corpo du joueur si la file est créée, ou place le joueur dans une file existante du groupe sinon.',
            'description': 'Place le joueur dans la file de RS',
            'bad_level': 'Le niveau de RS doit être entre 1 et 10',
            'queue_full': 'La file pour ce niveau de RS est pleine',
            'already_in': 'Vous êtes déjà dans la file niveau %d',
            'done': 'File pour RS%d :\n%s',
            'full_pings': '%s, la file est complète !',
        }
    }

class cmd_rsout (Bot9000Command):
    name = 'rsout'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('no_rs', player.language))
            return
        player.rsready = False
        player.save()
        players = [rsplayer for rsplayer in (rs.player1, rs.player2, rs.player3, rs.player4) if rsplayer not in (player, None)]
        if len(players) <= 0:
            await message.channel.send(cls.string('queue_deleted', player.language) % rs.level)
            rs.delete()
            return
        rs.resetplayers()
        if len(players) >= 1:
            rs.player1 = players[0]
        if len(players) >= 2:
            rs.player2 = players[1]
        if len(players) >= 3:
            rs.player3 = players[2]
        if len(players) >= 4:
            rs.player4 = players[3]
        rs.save()
        discorduser = discord.utils.get(message.guild.members, id=player.discordid)
        await message.channel.send(cls.string('done', player.language) % (discorduser.mention, rs.level))

    strings = {
        'FR': {
            'help': '**$rsout** : Sort de la file de RS en cours',
            'description': 'Sort le joueur de la file de RS',
            'no_rs': 'Vous n\'êtes dans aucune file de RS',
            'queue_deleted': 'La file RS%d a été supprimée',
            'done': '%s a quitté la file pour RS%d',
        }
    }

class cmd_rsshout (Bot9000Command):
    name = 'rsshout'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('no_rs', player.language))
            return
        role = discord.utils.get(message.guild.roles, id=group.rsroles()[rs.level - 1])
        if role is None:
            members = {update.player for update in PlayerUpdate.objects.filter(rslevel=rs.level)}
            discordusers = [discord.utils.get(message.guild.members, id=member.discordid) for member in members]
            pings = ' '.join([user.mention for user in discordusers])
            await message.channel.send(cls.string('response', player.language) % (pings, rs.level))
        else:
            await message.channel.send(cls.string('response', player.language) % (role.mention, rs.level))


    strings = {
        'FR': {
            'help': '**$rsshout** : Mentionne les joueurs inscrits pour le niveau de votre file actuelle',
            'description': 'Mentionne les joueurs inscrits pour le niveau de votre file actuelle',
            'no_rs': 'Vous n\'êtes dans aucune file de RS',
            'response': '%s, une RS%d va être lancée !',
        }
    }


class cmd_rsping (Bot9000Command):
    name = 'rsping'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('no_rs', player.language))
            return
        players = rs.players()
        queue = ''
        for rsplayer in players:
            discorduser = discord.utils.get(message.guild.members, id=player.discordid)
            queue += '- %s\n' % discorduser.mention
        await message.channel.send(cls.string('done', player.language) % (rs.level, queue))

    strings = {
        'FR': {
            'help': '**$rsping** : Mentionne tous les joueurs de la file',
            'description': 'Mentionne tous les joueurs de la file',
            'no_rs': 'Vous n\'êtes dans aucune file de RS',
            'done': 'File pour RS%d :\n%s',
        }
    }

class cmd_rsqueue (Bot9000Command):
    name = 'rsqueue'
    minimum_role = 'member'
    arguments = ('?level|l', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.level is not None:
            if not arguments.level.isdigit():
                await message.channel.send(cls.string('bad_level', player.language))
                return
            level = int(arguments.level)
            if not (1 <= level <= 10):
                await message.channel.send(cls.string('bad_level', player.language))
                return
            try:
                rs = RedStar.objects.get(group=group, level=level)
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('no_rs', player.language))
                return
        else:
            try:
                rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('no_rs', player.language))
                return
        users = [discord.utils.get(message.guild.members, id=rsplayer.discordid) for rsplayer in (rs.player1, rs.player2, rs.player3, rs.player4) if rsplayer is not None]
        players = '\n'.join(['- %s %s' % (discorduser.nick if discorduser.nick is not None else discorduser.name, ':white_check_mark:' if rsplayer.rsready else ':arrow_forward:') for rsplayer, discorduser in zip(rs.players(), users)])
        await message.channel.send(cls.string('done', player.language) % (rs.level, rs.corp.name, players))

    strings = {
        'FR': {
            'help': '**$rsqueue [-l <level>]** : Affiche la file pour le niveau de RS demandé. Si le niveau n\'est pas précisé, affiche la file dans laquelle vous êtes.',
            'description': 'Affiche une file de RS',
            'bad_level': 'Le niveau de RS doit être entre 1 et 10',
            'no_rs': 'Aucune file de RS ne correspond',
            'done': 'File pour RS%d (%s) :\n%s',
        }
    }

class cmd_rsready (Bot9000Command):
    name = 'rsready'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('no_rs', player.language))
            return
        if player.rsready:
            await message.channel.send(cls.string('already_ready', player.language))
            return
        player.rsready = True
        player.save()
        if any([rsplayer.rsready for rsplayer in rs.players()]):
            discorduser = discord.utils.get(message.guild.members, id=player.discordid)
            username = discorduser.nick if discorduser.nick is not None else discorduser.name
            await message.channel.send(cls.string('ready', player.language) % username)
        else:
            pings = ' '.join([discord.utils.get(message.guild.members, id=rsplayer.discordid).mention for rsplayer in rs.players()])
            discorduser = discord.utils.get(message.guild.members, id=player.discordid)
            username = discorduser.nick if discorduser.nick is not None else discorduser.name
            await message.channel.send(cls.string('ready_ping', player.language) % (pings, username))
        if all([rsplayer.rsready for rsplayer in rs.players()]):
            pings = ' '.join([discord.utils.get(message.guild.members, id=rsplayer.discordid).mention for rsplayer in rs.players()])
            await message.channel.send(cls.string('rs_run', player.language) % (pings, rs.level))
            rs.delete()

    strings = {
        'FR': {
            'help': '**$rsready** : Montre que vous êtes prêt pour la RS',
            'description': 'Montre que vous êtes prêt pour la RS',
            'no_rs': 'Vous n\'êtes dans aucune file de RS',
            'already_ready': 'Vous êtes déjà marqué comme prêt',
            'ready': '%s est prêt !',
            'ready_ping': '%s, %s est prêt !',
            'rs_run': '%s Lancement de la RS%d, tout le monde est prêt !',
        }
    }

class cmd_rsunready (Bot9000Command):
    name = 'rsunready'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('no_rs', player.language))
            return
        if not player.rsready:
            await message.channel.send(cls.string('not_ready', player.language))
            return
        player.rsready = False
        player.save()
        discorduser = discord.utils.get(message.guild.members, id=player.discordid)
        await message.channel.send(cls.string('unready', player.language) % (discorduser.nick if discorduser.nick is not None else discorduser.name))

    strings = {
        'FR': {
            'help': '**$rsunready** : Montre que vous n\'êtes plus prêt',
            'description': 'Montre que vous n\'êtes plus prêt',
            'no_rs': 'Vous n\'êtes dans aucune file de RS',
            'not_ready': 'Vous n\'êtes pas marqué prêt !',
            'unready': '%s n\'est plus prêt !',
        }
    }

class cmd_rsclearafk (Bot9000Command):
    name = 'rsclearafk'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not player.rsready:
            await message.channel.send(cls.string('not_ready', player.language))
            return
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('no_rs', player.language))
            return
        outplayers = [rsplayer for rsplayer in rs.players() if not rsplayer.ready and rsplayer != player]
        outusers = [discord.utils.get(message.guild.members, id=rsplayer.discordid) for rsplayer in outusers]
        rsplayers = [rsplayer for rsplayer in rs.players() if rsplayer not in outplayers]
        if len(players) >= 1:
            rs.player1 = players[0]
        if len(players) >= 2:
            rs.player2 = players[1]
        if len(players) >= 3:
            rs.player3 = players[2]
        if len(players) >= 4:
            rs.player4 = players[3]
        rs.save()

        player.rsready = False
        player.save()
        names = ' '.join([user.nick if user.nick is not None else user.name for user in outusers])
        await message.channel.send(cls.string('done', player.language) % names)

    strings = {
        'FR': {
            'help': '**$rsunready** : Montre que vous n\'êtes plus prêt',
            'description': 'Montre que vous n\'êtes plus prêt',
            'no_rs': 'Vous n\'êtes dans aucune file de RS',
            'not_ready': 'Vous n\'êtes pas marqué prêt !',
            'done': 'Supprimé %s de la file',
        }
    }

class cmd_outrs (Bot9000Command):
    name = 'outrs'
    minimum_role = 'member'
    arguments = ('level', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.level.isdigit():
            await message.channel.send(cls.string('bad_level', player.language))
            return
        level = int(arguments.level)
        if not 0 < level <= 10:
            await message.channel.send(cls.string('bad_level', player.language))
            return
        rss = RedStar.objects.get(level=level)


    strings = {
        'FR': {
            'help': '**$outrs <niveau>** : Liste les corporations où une file RS du niveau spécifié est active',
            'description': 'Liste les corporations où une file RS du niveau spécifié est active',
            'bad_level': 'Le niveau de RS doit être entre 1 et 10',
        }
    }"""

class _cmd_global_redstar (Bot9000Command):
    name = '__CMDGROUP_GLOBAL_redstar'
    minimum_role = 'nobody'
    arguments = ()
    parser = None

    @classmethod
    async def print_rsqueue(cls, rs, bot, shout):
        channels = rs.getchannels()
        queues = rs.getqueues()
        for i, player in enumerate(rs.players()):
            guild = discord.utils.get(bot.guilds, id=player.corp.group.discordid)
            channel = discord.utils.get(guild.channels, id=channels[i])
            roleid = player.corp.group.rsroles()[rs.level]
            if roleid is not None and shout:
                role = discord.utils.get(guild.roles, id=roleid)
                result = cls.string('introduction', player.language) % (role.mention, rs.id + 100, rs.corp.name)
            else:
                result = cls.string('introduction', player.language) % ('RS%d' % rs.level, rs.id + 100, rs.corp.name)
            for j, rsplayer in enumerate(rs.players()):
                result += cls.string('line', player.language) % ((':white_check_mark:' if rsplayer.rsready else ':black_square_button:'), j + 1, rsplayer.corp.group.name, rsplayer.name)
            queuemsg = await channel.send(result)
            latestid = queues[i]
            if latestid >= 0:
                latest = await channel.fetch_message(latestid)
                await latest.delete()
            queues[i] = queuemsg.id
        rs.setqueues(queues)
        rs.save()


    @classmethod
    async def rsqueue_full(cls, rs, bot):
        channels = rs.getchannels()
        for i, player in enumerate(rs.players()):
            if not player.rsready:
                guild = discord.utils.get(bot.guilds, id=player.corp.group.discordid)
                channel = discord.utils.get(guild.channels, id=channels[i])
                discorduser = discord.utils.get(guild.members, id=player.discordid)
                await channel.send(cls.string('full', player.language) % (discorduser.mention))

    @classmethod
    async def run_rs(cls, rs, bot):
        channels = rs.getchannels()
        for i, player in enumerate(rs.players()):
            guild = discord.utils.get(bot.guilds, id=player.corp.group.discordid)
            channel = discord.utils.get(guild.channels, id=channels[i])
            discorduser = discord.utils.get(guild.members, id=player.discordid)
            await channel.send(cls.string('run', player.language) % (discorduser.mention, rs.corp.name))

    strings = {
        'FR': {
            'introduction': '%s #%d [%s] :\n',
            'line': '%s %d- [%s] **%s**\n',
            'full': '%s, votre RS est prête à être lancée, utilisez $rsready pour vous signaler comme prêt',
            'run': '%s, tout le monde est prêt, votre RS est imminente dans la corporation %s',
        }
    }

class cmd_rslist (Bot9000Command):
    name = 'rslist'
    minimum_role = 'member'
    arguments = ('level', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.level.isdigit():
            await message.channel.send(cls.string('bad_level', player.language))
            return
        level = int(arguments.level)
        if not 0 < level <= 10:
            await message.channel.send(cls.string('bad_level', player.language))
            return
        rss = RedStar.objects.filter(level=level)
        if len(rss) == 0:
            await message.channel.send(cls.string('no_rs', player.language) % level)
        else:
            result = cls.string('introduction', player.language) % level
            for rs in rss:
                result += cls.string('line', player.language) % (rs.id + 100, rs.corp.name, len(rs.players()))
            await message.channel.send(result)

    strings = {
        'FR': {
            'help': '**$rslist <niveau>** : Liste les files de RS actives du niveau spécifié',
            'description': 'Liste les files de RS actives du niveau spécifié',
            'bad_level': 'Le niveau de RS doit être entre 1 et 10',
            'no_rs': 'Il n\'y a aucune file RS%d active',
            'introduction': 'Files pour RS%d :\n',
            'line': '#%d [%s] : %d / 4\n',
        }
    }

class cmd_rsin (Bot9000Command):
    name = 'rsin'
    minimum_role = 'member'
    arguments = ('id', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            testrs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
            await message.channel.send(cls.string('already_queued', player.language))
            return
        except ObjectDoesNotExist:
            pass
        if not arguments.id.isdigit():
            await message.channel.send(cls.string('bad_format', player.language))
            return
        id = int(arguments.id)
        if 0 < id <= 10:
            if id > player.rslevel():
                await message.channel.send(cls.string('higher_level', player.language) % (id, player.rslevel()))
                return
            try:
                rs = RedStar.objects.get(corp__group=player.corp.group, level=id)
                if len(rs.players()) >= 4:
                    rs = RedStar(level=id, corp=player.corp)
            except ObjectDoesNotExist:
                rs = RedStar(level=id, corp=player.corp)
            rs.addplayer(player, message.channel)
            rs.save()
        elif id > 100:
            id -= 100
            try:
                rs = RedStar.objects.get(id=id)
                if len(rs.players()) >= 4:
                    await message.channel.send(cls.string('rs_full', player.language) % id)
                    return
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('bad_id', player.language) % id)
                return
            if rs.level > player.rslevel():
                await message.channel.send(cls.string('higher_level', player.language) % (rs.level, player.rslevel()))
                return
            rs.addplayer(player, message.channel)
            rs.save()
        else:
            await message.channel.send(cls.string('bad_range', player.language))
            return
        await _cmd_global_redstar.print_rsqueue(rs, bot, len(rs.players()) == 1)
        if len(rs.players()) == 4:
            await _cmd_global_redstar.rsqueue_full(rs, bot)

    strings = {
        'FR': {
            'help': '**$rslist <niveau/id>** : Intègre ou crée la file RS du niveau spécifié dans votre corporation, ou rejoint celle du numéro donné par $rslist (les IDs de RS seront tous supérieurs à 100)',
            'description': 'Crée ou intègre une file de RS',
            'already_queued': 'Vous faites déjà partie d\'une autre file. Utilisez $rsout d\'abord pour la quitter',
            'bad_format': 'Le niveau ou l\'ID doit être un nombre entier',
            'bad_range': 'Les niveaux de RS sont entre 1 et 10, et les IDs de RS seront toujours supérieurs à 100 (vous pouvez les consulter avec $rslist)',
            'bad_id': 'La RS #%d n\'existe pas',
            'higher_level': 'Vous tentez de rejoindre une RS%d alors que votre niveau est RS%d',
            'rs_full': 'La RS #%d est complète',
        }
    }

class cmd_rsout (Bot9000Command):
    name = 'rsout'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        rs.removeplayer(player)
        rs.save()
        player.rsready = False
        player.save()
        await message.channel.send(cls.string('done', player.language) % (rs.level, rs.id + 100))
        if len(rs.players()) == 0:
            rs.delete()
        else:
            await _cmd_global_redstar.print_rsqueue(rs, bot, False)

    strings = {
        'FR': {
            'help': '**$rsout** : Sort de la file de RS dans laquelle vous êtes',
            'description': 'Sort de la file de RS dans laquelle vous êtes',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
            'done': 'Vous avez été retiré de la file RS%d #%d',
        }
    }

class cmd_rsshout (Bot9000Command):
    name = 'rsshout'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        await _cmd_global_redstar.print_rsqueue(rs, bot, True)

    strings = {
        'FR': {
            'help': '**$rsshout** : Mentionne les joueurs du niveau de RS correspondant sur les serveurs des joueurs de la file',
            'description': 'Mentionne les joueurs du niveau de RS correspondant sur les serveurs des joueurs de la file',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
        }
    }

class cmd_rsready (Bot9000Command):
    name = 'rsready'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        player.rsready = True
        player.save()
        if len([rsplayer for rsplayer in rs.players() if rsplayer.rsready]) == 1 and len(rs.players()) > 1:
            await _cmd_global_redstar.rsqueue_full(rs, bot)
        await _cmd_global_redstar.print_rsqueue(rs, bot, False)
        if all([rsplayer.rsready for rsplayer in rs.players()]):
            await _cmd_global_redstar.run_rs(rs, bot)
            for rsplayer in rs.players():
                rsplayer.rsready = False
                rsplayer.save()
            rs.delete()

    strings = {
        'FR': {
            'help': '**$rsready** : Vous signale comme prêt pour lancer la RS',
            'description': 'Vous signale comme prêt pour lancer la RS',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
        }
    }

class cmd_rsmsg (Bot9000Command):
    name = 'rsmsg'
    minimum_role = 'member'
    arguments = ('message', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        channels = rs.getchannels()
        for i, player in enumerate(rs.players()):
            guild = discord.utils.get(bot.guilds, id=player.corp.group.discordid)
            channel = discord.utils.get(guild.channels, id=channels[i])
            discorduser = discord.utils.get(guild.members, id=player.discordid)
            await channel.send('%s : %s' % (discorduser.mention, arguments.message))

    strings = {
        'FR': {
            'help': '**$rsmsg <message>** : Envoie un message à tous les joueurs de la file en cours',
            'description': 'Envoie un message à tous les joueurs de la file en cours',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
        }
    }

class cmd_rsunready (Bot9000Command):
    name = 'rsunready'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        player.rsready = False
        player.save()
        await _cmd_global_redstar.print_rsqueue(rs, bot, False)

    strings = {
        'FR': {
            'help': '**$rsunready** : Signifie que vous n\'êtes plus prêt pour la RS',
            'description': 'Signifie que vous n\'êtes plus prêt pour la RS',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
        }
    }

class cmd_rskick (Bot9000Command):
    name = 'rskick'
    minimum_role = 'member'
    arguments = ('number', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        if not arguments.number.isdigit():
            await message.channel.send(cls.string('not_a_number', player.language))
            return
        number = int(arguments.number)
        if not 1 <= number <= 4:
            await message.channel.send(cls.string('not_a_number', player.language))
            return
        kicked = rs.players()[number - 1]
        rs.removeplayer(kicked)
        rs.save()
        if len(rs.players()) == 0:
            rs.delete()
        else:
            await _cmd_global_redstar.print_rsqueue(rs, bot, False)

    strings = {
        'FR': {
            'help': '**$rskick <numéro>** : Expulse un joueur de la file de RS, en donnant le numéro indiqué sur la file (vois $rsqueue)',
            'description': 'Expulse un joueur de la file de RS',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
            'not_a_number': 'Le numéro doit être un nombre entre 1 et 4, et doit être le numéro du joueur à expulser sur la file (voir $rsqueue)',
        }
    }

class cmd_rsqueue (Bot9000Command):
    name = 'rsqueue'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            rs = RedStar.objects.get(Q(player1=player) | Q(player2=player) | Q(player3=player) | Q(player4=player))
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_in_rs', player.language))
            return
        await _cmd_global_redstar.print_rsqueue(rs, bot, False)

    strings = {
        'FR': {
            'help': '**$rsqueue** : Affiche votre file de RS actuelle',
            'description': 'Affiche votre file de RS actuelle',
            'not_in_rs': 'Vous n\'êtes actuellement dans aucune file de RS',
        }
    }
