# -*- coding:utf-8 -*-

import discord
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import *
from main.models import *
from ..base import Bot9000Command


class cmd_rsin (Bot9000Command):
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
        await message.channel.send(cls.string('done', player.language) % (rs.level, players))

    strings = {
        'FR': {
            'help': '**$rsqueue [-l <level>]** : Affiche la file pour le niveau de RS demandé. Si le niveau n\'est pas précisé, affiche la file dans laquelle vous êtes.',
            'description': 'Affiche une file de RS',
            'bad_level': 'Le niveau de RS doit être entre 1 et 10',
            'no_rs': 'Aucune file de RS ne correspond',
            'done': 'File pour RS%d :\n%s',
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
